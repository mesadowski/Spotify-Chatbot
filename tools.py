#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 23 06:46:44 2025

@author: michaelsadowski
"""

tools =[
    {
        "type": "function",
        "name": "add_to_playlist",
        "description": "Function to add several Spotify tracks to a Spotify playlist. If the playlist is new, create it before adding the tracks. ",
        "parameters": {
            "type": "object",
            "properties": {
                "new_flag": {
                    "type": "boolean",
                    "description": "True when playlist is new, and False when playlist already exists."
                    },
                "playlist_name": { 
                    "type": "string",
                    "description": "The name of the Spotify playlist the user wants to use."
                    },
                "tracks": {
                    "type": "array",
                    "description": "A list of tracks to be added to the playlist.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "track_name": {
                                "type": "string",
                                "description": "The name of the track or song."
                            },
                            "artist": {
                                "type": "string",
                                "description": "The artist that recorded the track or song."
                            }
                        },
                        "required": ["track_name", "artist"]
                    }
                }
            },
            "required": ["new_flag","playlist_name", "tracks"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "add_to_queue",
        "description": "Add a several Spotify tracks to the user's queue for playback.",
        "parameters": {
            "type": "object",
            "properties": {
                "tracks": {
                    "type": "array",
                    "description": "A list of tracks to be added to the queue.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "track_name": {
                                "type": "string",
                                "description": "The name of the track or song."
                            },
                            "artist": {
                                "type": "string",
                                "description": "The artist that recorded the track or song."
                            }
                        },
                        "required": ["track_name", "artist"]
                    }
                }
            },
            "required": ["tracks"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "pause",
        "description": "Pause or stop playing on the current device. The user will use words like 'pause', 'pause play' or 'stop'"    
    },
    {
        "type": "function",
        "name": "start",
        "description": "Start playing on the current device. The user will use words like 'start', 'play', 'play now' or 'go'"    
    },
    {
        "type": "function",
        "name": "get_playlists",
        "description": "Get the user's private playlists from Spotify."    
    },
    {
        "type": "function",
        "name": "reset",
        "description": "Clear all messages and start again. The user wants to start over with a fresh chat session. The user will use words like 'reset, or 'clear history'"    
    },
    {
        "type": "function",
        "name": "clear_queue",
        "description": "Clear all tracks from the queue. The user will use words like 'clear queue'."    
    },
    {
        "type": "function",
        "name": "top_tracks",
        "description": "Get the top (or best) tracks for an artist from Spotify. This function should be used to get the top tracks, rather than general knowledge.",  
        "parameters": {
            "type": "object",
            "properties": {
                "artist_name": {
                    "type": "string",
                    "description": "The name of the artist the user provided.",
                },
            },
            "required": ["artist_name"]
        },
    },
    {
        "type": "function",
        "name": "playlist_tracks",
        "description": "Get the tracks in one Spotify playlist .",  
        "parameters": {
            "type": "object",
            "properties": {
                "playlist_name": {
                    "type": "string",
                    "description": "The name of the playlist the user provided.",
                },
            },
            "required": ["playlist_name"]
        },
    
    },
    {
       "type": "function",
       "name": "album_tracks",
       "description": "Find the tracks on an album.",
       "parameters": {
          "type": "object",
          "properties": {
              "album": {
                  "type": "array",
                  "description": "An album whose tracks the user wants to look up.",
                  "items": {
                      "type": "object",
                      "properties": {
                          "album_name": {
                              "type": "string",
                              "description": "The name of the album."
                          },
                          "artist": {
                              "type": "string",
                              "description": "The main artist that recorded the album."
                          }
                      },
                      "required": ["album_name", "artist"]
                  }
              }
          },
          "required": ["album"],
          "additionalProperties": False
      },
  },
    {
       "type": "function",
       "name": "play_track",
       "description": "Play a single Spotify track.",
       "parameters": {
          "type": "object",
          "properties": {
              "tracks": {
                  "type": "array",
                  "description": "A list of tracks to be added to the queue. There should only be one track in this case.",
                  "items": {
                      "type": "object",
                      "properties": {
                          "track_name": {
                              "type": "string",
                              "description": "The name of the track or song."
                          },
                          "artist": {
                              "type": "string",
                              "description": "The artist that recorded the track or song."
                          }
                      },
                      "required": ["track_name", "artist"]
                  }
              }
          },
          "required": ["tracks"],
          "additionalProperties": False
      }
  },
    {
       "type": "function",
       "name": "play_album",
       "description": "Play a single Spotify album.",
       "parameters": {
          "type": "object",
          "properties": {
              "albums": {
                  "type": "array",
                  "description": "A list of albums to play. There should only be one album in this case.",
                  "items": {
                      "type": "object",
                      "properties": {
                          "album_name": {
                              "type": "string",
                              "description": "The name of the album."
                          },
                          "artist": {
                              "type": "string",
                              "description": "The artist that recorded the album."
                          }
                      },
                      "required": ["album_name", "artist"]
                  }
              }
          },
          "required": ["albums"],
          "additionalProperties": False
      }
  },

    {
        "type": "function",
        "name": "play_playlist",
        "description": "Play one Spotify playlist .",  
        "parameters": {
            "type": "object",
            "properties": {
                "playlist_name": {
                    "type": "string",
                    "description": "The name of the playlist the user wants to play.",
                },
            },
            "required": ["playlist_name"]
        },
    
    },
    
]
