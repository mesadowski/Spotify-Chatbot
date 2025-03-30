#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 12:43:40 2025

@author: michaelsadowski
"""

import json
from tenacity import retry, wait_random_exponential, stop_after_attempt
from difflib import SequenceMatcher

GPT_MODEL = 'gpt-4o-mini'

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_request(openai_client, messages, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        response = openai_client.responses.create(
            model=model,
            input=messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=0.3
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

def create_track_list(sp,args):
    
    rec_list = args['tracks']
    
    tracks_to_add = []
    track_ids_to_add = []
    
    for rec in rec_list:

        artist = rec['artist']
        track = rec['track_name']
        query = f"track:{track} artist:{artist}"  
    
        results = sp.search(q=query, type='track', limit=5) # Limit is optional, defaults to 20  
        
        print(f'search results = {results}')
        
        if results['tracks']['items'] != []:
            artist = results['tracks']['items'][0]['album']['artists'][0]['name']
            song_name = results['tracks']['items'][0]['name']
            id= results['tracks']['items'][0]['id']

            tracks_to_add += (id,artist,song_name)
            track_ids_to_add.append(id)  
    return track_ids_to_add, tracks_to_add

def extract_response_details(response):
    """Extracts response text and function call details from OpenAI API response."""
    response_text = None
    function_name = None
    function_args = None

    for item in response.output:  # Accessing the output list
        if item.type == "message" and hasattr(item, "content"):  # Check if it's a text message
            response_text = " ".join([text_item.text for text_item in item.content if hasattr(text_item, "text")])
        elif item.type == "function_call":  # Check if it's a function call
            function_name = item.name
            function_args = json.loads(item.arguments)  # Parse JSON arguments

    return response_text, function_name, function_args

def clear_queue(sp):
    currently_playing = sp.currently_playing()
    queue = sp.queue()
    
    if queue['queue'] and currently_playing: # skip through queue. There is no API call to clear the queue directly
        for i in range(len(queue['queue'])-1):
            sp.next_track()
        return True
    else: # queue might have been empty
        return False

def add_items_to_queue(sp,args):   
    track_ids_to_add, tracks_to_add = create_track_list(sp,args)
    devices = sp.devices()['devices'][0]
   
    if devices['is_active'] and track_ids_to_add != []:
        for t in track_ids_to_add:              
            sp.add_to_queue(t, device_id=None)  
        return True
    else:
        return False
    
def top_tracks(sp,artist):
    query = f"artist:{artist['artist_name']}"  
   
    search_results = sp.search(q=query, type='artist', limit=3) # Limit is optional, defaults to 20  
    print(f'Search results: {search_results}') 
    track_list = []
    tracks_string = ''
    if search_results['artists']['total'] != 0:
        artist_id = search_results['artists']['items'][0]['id']
        results = sp.artist_top_tracks(artist_id)
        if results['tracks']!= []:
            for r in results['tracks']:          
                track_id = r['id']
                track_name = r['name']
                track_list.append((track_name,track_id))   
                tracks_string += track_name + '  \n'
        return tracks_string, track_list
    else:
        print("Can't find artist id.")
        return tracks_string, track_list

def playlist_tracks(sp,playlist,user_playlists):
    # get user playlists ad try to match the name. Close enough is OK
    playlist_id = ''
    for p in user_playlists:
        if SequenceMatcher(None, p[0], playlist['playlist_name']).ratio()> 0.85:
           playlist_id = p[1]
           break
       
    track_list = []
    tracks_string = ''
    if playlist_id != '':
        results = sp.playlist_tracks(playlist_id)

        if results['items']!= []:
            for r in results['items']:          
                track_id = r['track']['id']
                track_name = r['track']['name']
                track_list.append((track_name,track_id))   
                tracks_string += track_name + '  \n'
    return tracks_string, track_list
    

def album_tracks(sp,args):
    query = f"album:{args['album'][0]['album_name']} artist:{args['album'][0]['artist']}"  
   
    search_results = sp.search(q=query, type='album', limit=2) # Limit is optional, defaults to 20  
    print(f"search_results = {search_results}")
    if search_results['albums']['items'] == []:
        return '',[]
    else:
        album_id = search_results['albums']['items'][0]['id']
        results = sp.album_tracks(album_id)
        track_list = []
        tracks_string = ''
        if results['items']!= []:
            for r in results['items']:          
                track_id = r['id']
                track_name = r['name']
                track_list.append((track_name,track_id))   
                tracks_string += track_name + '  \n'
        return tracks_string, track_list

def pause(sp):
    devices = sp.devices()
    currently_playing = sp.currently_playing()
    
    if devices['devices'] == []:
        return False    
    elif devices['devices'][0]['is_active'] and currently_playing['is_playing']==True:     
        result = sp.pause_playback()
        return True
    else:
        return False

def start(sp):
    devices = sp.devices()
    currently_playing = sp.currently_playing()

    if devices['devices'] == []:
        return False    
    elif devices['devices'][0]['is_active'] and currently_playing['is_playing']==False: 
        result = sp.start_playback()
        return True
    else:
        return False

def play_track(sp,args):
    track_ids_to_add, tracks_to_add = create_track_list(sp,args)
    print(f'track IDs to add: {track_ids_to_add}')
    devices = sp.devices()
    #print(devices)
    #currently_playing = sp.currently_playing()    
   
    if devices['devices'] == []:
        return False    
    elif devices['devices'][0]['is_active'] and len(track_ids_to_add) == 1:
        uri = f'spotify:track:{track_ids_to_add[0]}'
        print(f'uri to add: {uri}')
        sp.start_playback(uris = [uri])
        return True
    else:
        return False
    
def play_playlist(sp,args):
    #get all playists
    playlist_string, playlist_list = get_playlists(sp)  
    print(playlist_list)
    
    # find the desired playlist
    pid = ''
    for p in playlist_list:
       if p[0] == args['playlist_name']:
           pid = p[1]
           print(f'found playlist {pid}')
           break
       
    devices = sp.devices()
    #currently_playing = sp.currently_playing()   

    if devices['devices'] == []:
        return False      
    if devices['devices'][0]['is_active'] and pid != '':
        print('starting playback')
        sp.start_playback(context_uri = "spotify:playlist:"+pid)
        return True
    else:
        return False
    
def play_album(sp,args):
   query = f"album:{args['albums'][0]['album_name']} artist:{args['albums'][0]['artist']}"  
  
   search_results = sp.search(q=query, type='album', limit=2) 
   print(f"search_results = {search_results}")
   if search_results['albums']['items'] != []:
       devices = sp.devices()
       if devices['devices'] == []:
           return False  

       #currently_playing = sp.currently_playing()   
       elif devices['devices'][0]['is_active']:
           print('starting playback')
           album_id = search_results['albums']['items'][0]['id']
           context_uri = "spotify:album:"+album_id
           sp.start_playback(context_uri = context_uri)
           return True
   else:
       return False

def get_playlists(sp):
    result = sp.current_user_playlists(limit=50)
    playlist_list = []
    playlist_string = ''
    for p in result['items']:
        playlist_list.append((p['name'],p['id']))    
        playlist_string += p['name'] + '  \n'
    return playlist_string, playlist_list

def add_items_to_playlist(sp,args):    
    
    track_ids_to_add, tracks_to_add = create_track_list(sp,args)
    print(f'track_ids_to_add = {track_ids_to_add}')
    
    playlist_name = args['playlist_name']
    
    new_list = args['new_flag']
    
    user_profile = sp.current_user()
    user_id = user_profile['id']
    #print(user_profile)
    
    if new_list: #create new list if needed
        playlist = sp.user_playlist_create(user=user_id,name=playlist_name,public=False,collaborative=False,description='My new playlist')  
        pid = playlist['id']
        delta_tracks = set(track_ids_to_add)
        print(f'delta tracks = {delta_tracks}')
    else:   # add to an existing list
        playlists = sp.user_playlists(user_id)
        for p in playlists['items']:
           if p['name'] == playlist_name:
               pid = p['id']
               break
        print(f'playlist id found: {pid}')
        if pid:   # found the playlist
            existing_tracks = sp.user_playlist_tracks(user=user_id, playlist_id=pid)
            existing_tracks = sp.playlist_tracks(playlist_id=pid)
            
            existing_tracks_set = set()
            for i in existing_tracks['items']:
                track_id = i['track']['id']
                existing_tracks_set.add(track_id)
            tracks_ids_to_add_set = set(track_ids_to_add)
                
            delta_tracks = tracks_ids_to_add_set - existing_tracks_set
            print(f'delta tracks = {delta_tracks}')
        else:   # could not find the play list
            return False
                   
    if delta_tracks != set():
        sp.playlist_add_items(playlist_id=pid, items=list(delta_tracks))  # add items
        return True
    else: return False

