The documentation of a tool from our ToolFlow dataset, which has 1757 tokens.
```txt
API name: GET_tv_tv_id
### API url
https://api.themoviedb.org/3/tv/{tv_id}
### Request type
GET
### Description
Get the primary TV show details by id.
### Parameter
No extra parameter, just replace the `{variable}` in the url path with actual value.
### Execution result specification
{
    "description": "str",
    "content": {
        "application/json": {
            "schema": {
                "type": "str",
                "properties": {
                    "backdrop_path": {
                        "title": "str",
                        "nullable": "bool",
                        "type": "str"
                    },
                    "created_by": {
                        "type": "str",
                        "items": {
                            "type": "str",
                            "properties": {
                                "id": {
                                    "type": "str"
                                },
                                "credit_id": {
                                    "type": "str"
                                },
                                "name": {
                                    "type": "str"
                                },
                                "gender": {
                                    "type": "str"
                                },
                                "profile_path": {
                                    "type": "str"
                                }
                            }
                        }
                    },
                    "episode_run_time": {
                        "type": "str",
                        "items": {
                            "type": "str"
                        }
                    },
                    "first_air_date": {
                        "type": "str"
                    },
                    "genres": {
                        "type": "str",
                        "items": {
                            "type": "str",
                            "properties": {
                                "id": {
                                    "type": "str"
                                },
                                "name": {
                                    "type": "str"
                                }
                            }
                        }
                    },
                    "homepage": {
                        "type": "str"
                    },
                    "id": {
                        "type": "str"
                    },
                    "in_production": {
                        "type": "str"
                    },
                    "languages": {
                        "type": "str",
                        "items": {
                            "type": "str"
                        }
                    },
                    "last_air_date": {
                        "type": "str"
                    },
                    "last_episode_to_air": {
                        "type": "str",
                        "properties": {
                            "air_date": {
                                "type": "str"
                            },
                            "episode_number": {
                                "type": "str"
                            },
                            "id": {
                                "type": "str"
                            },
                            "name": {
                                "type": "str"
                            },
                            "overview": {
                                "type": "str"
                            },
                            "production_code": {
                                "type": "str"
                            },
                            "season_number": {
                                "type": "str"
                            },
                            "show_id": {
                                "type": "str"
                            },
                            "still_path": {
                                "type": "str"
                            },
                            "vote_average": {
                                "type": "str"
                            },
                            "vote_count": {
                                "type": "str"
                            }
                        }
                    },
                    "name": {
                        "type": "str"
                    },
                    "next_episode_to_air": {
                        "nullable": "bool"
                    },
                    "networks": {
                        "type": "str",
                        "items": {
                            "type": "str",
                            "properties": {
                                "name": {
                                    "type": "str"
                                },
                                "id": {
                                    "type": "str"
                                },
                                "logo_path": {
                                    "type": "str"
                                },
                                "origin_country": {
                                    "type": "str"
                                }
                            }
                        }
                    },
                    "number_of_episodes": {
                        "type": "str"
                    },
                    "number_of_seasons": {
                        "type": "str"
                    },
                    "origin_country": {
                        "type": "str",
                        "items": {
                            "type": "str"
                        }
                    },
                    "original_language": {
                        "type": "str"
                    },
                    "original_name": {
                        "type": "str"
                    },
                    "overview": {
                        "type": "str"
                    },
                    "popularity": {
                        "type": "str"
                    },
                    "poster_path": {
                        "title": "str",
                        "nullable": "bool",
                        "type": "str"
                    },
                    "production_companies": {
                        "type": "str",
                        "items": {
                            "type": "str",
                            "properties": {
                                "id": {
                                    "type": "str"
                                },
                                "logo_path": {
                                    "nullable": "bool",
                                    "type": "str"
                                },
                                "name": {
                                    "type": "str"
                                },
                                "origin_country": {
                                    "type": "str"
                                }
                            }
                        }
                    },
                    "seasons": {
                        "type": "str",
                        "items": {
                            "type": "str",
                            "properties": {
                                "air_date": {
                                    "type": "str"
                                },
                                "episode_count": {
                                    "type": "str"
                                },
                                "id": {
                                    "type": "str"
                                },
                                "name": {
                                    "type": "str"
                                },
                                "overview": {
                                    "type": "str"
                                },
                                "poster_path": {
                                    "type": "str"
                                },
                                "season_number": {
                                    "type": "str"
                                }
                            }
                        }
                    },
                    "status": {
                        "type": "str"
                    },
                    "type": {
                        "type": "str"
                    },
                    "vote_average": {
                        "type": "str"
                    },
                    "vote_count": {
                        "type": "str"
                    }
                }
            },
            "examples": {
                "response": {
                    "value": {
                        "backdrop_path": "str",
                        "created_by": [
                            {
                                "id": "int",
                                "credit_id": "str",
                                "name": "str",
                                "gender": "int",
                                "profile_path": "str"
                            }
                        ],
                        "episode_run_time": [
                            "int"
                        ],
                        "first_air_date": "str",
                        "genres": [
                            {
                                "id": "int",
                                "name": "str"
                            }
                        ],
                        "homepage": "str",
                        "id": "int",
                        "in_production": "bool",
                        "languages": [
                            "str"
                        ],
                        "last_air_date": "str",
                        "last_episode_to_air": {
                            "air_date": "str",
                            "episode_number": "int",
                            "id": "int",
                            "name": "str",
                            "overview": "str",
                            "production_code": "str",
                            "season_number": "int",
                            "show_id": "int",
                            "still_path": "str",
                            "vote_average": "float",
                            "vote_count": "int"
                        },
                        "name": "str",
                        "next_episode_to_air": "NoneType",
                        "networks": [
                            {
                                "name": "str",
                                "id": "int",
                                "logo_path": "str",
                                "origin_country": "str"
                            }
                        ],
                        "number_of_episodes": "int",
                        "number_of_seasons": "int",
                        "origin_country": [
                            "str"
                        ],
                        "original_language": "str",
                        "original_name": "str",
                        "overview": "str",
                        "popularity": "float",
                        "poster_path": "str",
                        "production_companies": [
                            {
                                "id": "int",
                                "logo_path": "str",
                                "name": "str",
                                "origin_country": "str"
                            }
                        ],
                        "seasons": [
                            {
                                "air_date": "str",
                                "episode_count": "int",
                                "id": "int",
                                "name": "str",
                                "overview": "str",
                                "poster_path": "str",
                                "season_number": "int"
                            }
                        ],
                        "status": "str",
                        "type": "str",
                        "vote_average": "float",
                        "vote_count": "int"
                    }
                }
            }
        }
    }
}
### Request body
"This API do not need the request body when calling."
```

The documentation of a tool from the ToolBench dataset, which has only 276 tokens.
```json
{
  "name": "togo420_our_catalogue",
  "url": "https://togo420.p.rapidapi.com/catalogue",
  "description": "This endpoint allows developers to view our inventory catalogue with inventory quantities, product images, product descriptions, etc.",
  "method": "GET",
  "required_parameters": [],
  "optional_parameters": [],
  "code": "import requests\n\nurl = \"https://togo420.p.rapidapi.com/catalogue\"\n\nheaders = {\n            \"X-RapidAPI-Key\": \"SIGN-UP-FOR-KEY\",\n            \"X-RapidAPI-Host\": \"togo420.p.rapidapi.com\"\n        }\n\nresponse = requests.get(url, headers=headers)\nprint(response.json())\n",
  "convert_code": "import requests\n\nurl = \"https://togo420.p.rapidapi.com/catalogue\"\n\nheaders = {\n            \"X-RapidAPI-Key\": \"SIGN-UP-FOR-KEY\",\n            \"X-RapidAPI-Host\": \"togo420.p.rapidapi.com\"\n        }\n\nresponse = requests.get(url, headers=headers)\nprint(response.json())\n",
  "test_endpoint": {
    "message": "Missing Authentication Token"
  }
}
```
