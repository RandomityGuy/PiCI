# PiCI
A very tiny Heroku clone that I use to deploy and control apps on my Raspberry Pi. I am only sharing this here because I think its really cool.

## Running
Just do `python main.py`

## Commands
`help`: show help  
`load <app.json>`: build app.json  
`apps`: list available apps  
`list`: list running apps  
`start <app_name>`: start app with name <app_name>  
`stop <app_name>`: stop app with name <app_name>  
`build <app_name> [-s]`: build app with name <app_name>, -s: silent  
`tail <app_name>`: tail log of app with name <app_name>  
`output <app_name>`: output log of app with name <app_name>  
`error <app_name>`: error log of app with name <app_name>  
`exit`: exit PiCI  

## Info
This program also generates nginx configs if the app.json specifies any domain  
The apps are stored and built in .pici/apps/<appname>  
App logs are stored in .pici/configs  

## Sample Config app.json
```json
{
  "name": "My Sample App",
  "git": "https://github.com/Test/Sample.git",
  "build_command": "pip install -r requirements.txt",
  "start_command": "python sample.py",
  "domains": [ 
    {
      "domain": "sampleapp.example.com",
      "outport": 80,
      "localport": 5050
    }
  ]
}
```
