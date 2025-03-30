#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: michaelsadowski
"""


import streamlit as st
import os

from openai import OpenAI

import toml
from spotipy import Spotify
from spotipy.cache_handler import CacheHandler
from spotipy.exceptions import SpotifyOauthError
from spotipy.oauth2 import SpotifyOAuth

# Load the configuration from the TOML file
config = toml.load("./config.toml")

from utils import play_album, play_playlist, album_tracks,chat_request, extract_response_details, clear_queue, add_items_to_queue, top_tracks, playlist_tracks, pause, start, play_track, get_playlists, add_items_to_playlist
from tools import tools

#OPENAI_API_KEY = <insert key here, or better use the envionment variable below>
OPENAI_API_KEY = os.environ['OPENAI_API_KEY'] 

openai_client = OpenAI(api_key=OPENAI_API_KEY)

class StreamlitCacheHandler(CacheHandler):
    def __init__(self):
        self.session_id = st.session_state.get("session_id")

    def get_cached_token(self):
        return st.session_state.get("spotipy_token")

    def save_token_to_cache(self, token_info):
        st.session_state["spotipy_token"] = token_info

def get_auth_manager():
    """
    Returns a spotipy.oauth2.SpotifyOAuth object.
    """
    return SpotifyOAuth(**config["spotipy"], cache_handler=StreamlitCacheHandler())

def callback():
    code = st.query_params.get("code")
    if code:
        try:
            token_info = get_auth_manager().get_access_token(code)
        except SpotifyOauthError:
            pass
    del st.query_params["code"]
    
def output(role, content, extra_arg=None):  #output to screen and to messages
    #st.session_state.messages.append({"role": role, "content": content+str(extra_arg).strip('[]')}) 
    print(f'role: {role}  content:{content}',flush=True)
    with st.chat_message(role):
        st.session_state.messages.append({"role": role, "content": content})
        st.write(content)
    return

background ="The user wants to control Spotify.\
            Use the tools functions provided to get information from Spotify or take actions in Spotify. If the user asks you to take actions in Spotify, \
            such as pause or start playback, do not just reply that you took the action--you should use the tools functions. If you are not certain what to do, or if you \
            don't have all information needed to call a tools function, ask the user for clarification or more details. If the user asks general questions about music then answer those concisely. But don't\
            answer questions that are not related to music."

st.set_page_config(page_title="SpotiBot")

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Spotify AI Control Chatbot")

st.markdown("I'm an AI chatbot that can control Spotify for you. Spotify must be running on the device you are using now. Ask me questions or give me commands such as:\
            'What were David Bowie's top songs', 'Add those songs to the queue' or 'pause play'. You can also ask me \
            general questions about music, e.g., 'Tell me about how Bowie and Lennon collaborated to write the song Fame.'")

st.sidebar.markdown(r"$\textsf{\Large Here are some ideas}$")    
st.sidebar.markdown("What were David Bowie's top tracks?")
st.sidebar.markdown("What are some less popular, but influential Neil Young songs. Make a playlist called Deep Neil with those songs.")
st.sidebar.markdown("What are all my playlists?")
st.sidebar.markdown("Play my _______ playlist")
st.sidebar.markdown("Play Outlandos D'Amour by the Police")
st.sidebar.markdown("What tracks are on Communique by Dire Straits?")
st.sidebar.markdown("What tracks are in my my playlist ______?")
st.sidebar.markdown("Pause (only works when the player on this device is active)")
st.sidebar.markdown("Start (only works when the player on this device is active)")
st.sidebar.markdown("Tell me about how Bowie and Lennon collaborated to write the song Fame.")
st.sidebar.markdown("Give me a list of the best Chillwave songs since 2010. (after the list is returned, ask to add them to a new playlist)")

if 'sp' in st.session_state:
    sp = st.session_state["sp"]    
else: 
    sp = Spotify(auth_manager=get_auth_manager())
    st.session_state["sp"] = sp

if st.query_params.get("code"):
    callback()

if "spotipy_token" not in st.session_state:
    if st.button("Log in to Spotify"):
        # prevents a new tab from being opened
        st.markdown(f'<meta http-equiv="refresh" content="0; '
                    f'url={sp.auth_manager.get_authorize_url()}"/>',
                    unsafe_allow_html=True)    

if "messages" not in st.session_state:
    st.session_state.messages = []  
    st.session_state.messages.append({"role": "system", "content": background})

for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])  
        
if "spotipy_token" in st.session_state: 
    if prompt := st.chat_input("What do you want me to do?"):
    
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
                    
        #print(st.session_state.messages,flush=True)
        
        response = chat_request(openai_client,st.session_state.messages, tools=tools, tool_choice="auto")
        
        #print(f'AI response: {response}',flush=True)
    
        response_text, function_name, function_args = extract_response_details(response)   
        
        print(f"Function Name: {function_name}",flush=True)
        print(f"Function Arguments: {function_args}",flush=True)
    
        if response_text != None:
            output(role="system", content=response_text)
        
        if not(function_name):
            # Nothing to do. Go back and get clarification
            pass
        
        elif function_name == 'album_tracks':
            tracks_string, tracks_list = album_tracks(sp,function_args)
            print(tracks_list)
            if tracks_string:
                with st.chat_message("system"):
                    st.session_state.messages.append({"role": "system", "content": f"These are the tracks: {tracks_string}"})         
                    st.write(f"The tracks on the album {function_args['album'][0]['album_name']} by {function_args['album'][0]['artist']} are:  \n")
                    for track in tracks_list:
                        st.write(f"[{track[0]}](spotify:track:{track[1]})")
            else:
                output(role="system", content="I wasn't able to find that album/artist combination. Please try again.") 
                
        elif function_name == 'play_track':
            result = play_track(sp,function_args)
            if result:  
                output(role="system", content=f"OK I successfully started the track {function_args['tracks'][0]['track_name']} by {function_args['tracks'][0]['artist']}.")
            else:
                output(role="system", content="I wasn't able to start that track. Please check your spelling ensure Spotify is running on this device.") 
                
        elif function_name == 'play_album':
            result = play_album(sp,function_args)
            print(function_args)
            if result:  
                output(role="system", content=f"OK I successfully started the album {function_args['albums'][0]['album_name']} by {function_args['albums'][0]['artist']}.")
            else:
                output(role="system", content="I wasn't able to start that album. Please check your spelling ensure Spotify is running on this device.") 

        elif function_name == 'clear_queue':
            output(role="system", content="Note: there is no clear queue function so as a workaround I'm going to try to skip through the whole queue.")
            result = clear_queue(sp)
            if result:  
                output(role="system", content="OK I think I successfully skipped the queue.")
            else:
                output(role="system", content="I wasn't able to clear the queue. Perhaps it was already empty or Spotify was not running on this device.")
                
        elif function_name == 'top_tracks':
            tracks_string, tracks_list = top_tracks(sp,function_args)
            print(tracks_list)
            print(function_args)
            if tracks_string:
                with st.chat_message("system"):
                    st.session_state.messages.append({"role": "system", "content": f"These are the tracks:   \n {tracks_string}"})     
                    st.write(f"The top tracks by {function_args['artist_name']} are:  \n")
                    for track in tracks_list:
                        st.write(f"[{track[0]}](spotify:track:{track[1]})")
            else:
                output(role="system", content="I wasn't able to look that up on Spotify.")
                
        elif function_name == 'add_to_playlist':
            result = add_items_to_playlist(sp,function_args)
            if result:
                output(role="system", content="OK I added those tracks to the playlist.")
            else:
                output(role="system", content="I had a problem adding those tracks to your playlist.")
                
        elif function_name == 'add_to_queue':
            output(role="system", content="OK I'm adding the tracks. This can take a minute.")
            result = add_items_to_queue(sp,function_args)
            if result:
                output(role="system", content="OK I added those tracks to your queue.")
            else:
                output(role="system", content="I had a problem adding those tracks to your queue. Please ensure Spotify is running on this device.")
                
        elif function_name == 'pause':
            result = pause(sp)
            if result:  
                output(role="system", content="OK I successfully paused playback.")
            else:
                output(role="system", content="I wasn't able to pause playback. Please ensure Spotify is running on this device.")
                
        elif function_name == 'start':
            result = start(sp)
            if result:  
                output(role="system", content="OK I successfully started playback.")
            else:
                output(role="system", content="I wasn't able to start playback. Please ensure Spotify is running on this device.") 
                
        elif function_name == 'get_playlists':
            playlist_string, playlist_list = get_playlists(sp)
            if playlist_string:      
                with st.chat_message("system"):
                    st.session_state.messages.append({"role": "system", "content": f"These are your current playlists:   \n {playlist_string}"})     
                    st.write("These are your current playlists:   \n")
                    for playlist in playlist_list:
                        st.write(f"[{playlist[0]}](spotify:playlist:{playlist[1]})")
            else:
                output(role="system", content="I wasn't able to get your playlists. Please ensure Spotify is running on this device.") 
                
        elif function_name == 'playlist_tracks':
            playlist_string,user_playlists = get_playlists(sp)
            tracks_string, tracks_list = playlist_tracks(sp,function_args,user_playlists)
            print(tracks_list)
            print(function_args)
            if tracks_string:
                with st.chat_message("system"):
                    st.session_state.messages.append({"role": "system", "content": f"These are the tracks:   \n {tracks_string}"})     
                    st.write(f"The tracks in the playlist {function_args['playlist_name']} are:   \n")
                    for track in tracks_list:
                        st.write(f"[{track[0]}](spotify:track:{track[1]})")
            else:
                output(role="system", content="I wasn't able to look that up on Spotify.")
                
        elif function_name == 'play_playlist':
            result = play_playlist(sp,function_args)
            if result:  
                output(role="system", content="OK I successfully started the playlist.")
            else:
                output(role="system", content="I wasn't able to start playback. Please check the playlist name and ensure Spotify is running on this device.") 
      
                
        elif function_name == "reset": #reset and clear all messages
            st.session_state.messages = []
            st.session_state.messages.append({"role": "system", "content": background})
        
    
    
