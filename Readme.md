# NAO for social robotics

Welcome

## Requirements 
Choregraph software -- [Installation manual](https://socialrobotics.atlassian.net/wiki/spaces/SIR2021/pages/2116911105/Choreographe).

SIC framework -- [Installation manual](https://socialrobotics.atlassian.net/wiki/spaces/SIR2021/pages/2116681729/SIC+framework)

Dialogoflow

In this repo, a variety of files can be found, most of which will be discussed in this Readme. Please note that most of the programs in this repo are not executable as stand-alone programs. Often they are to be used in combination with Docker and a handful of Java programs that are not included.  It does, however, resemble the progress we have made.

## Content

```base_template.py``` includes our main robot class. In the class ```BaseRobot``` the connection and control of Devices is managed. Speech recognition, Scripted conversation, connection to ```GPT3```, and gesture control.

```main.py``` contains the class ```MainFrame``` and it will act as our expermiment flow. It handles high-level control.

```bot-private-dialg.json``` is the file used for the Google Dialogflow API.

```Resources``` is used for Google Dialogflow.

## Config files

The config files are in ```JSON``` format. For every system of the robot, there is an indentation. Currently, two main configurations have been added to support our experiments. Introvert and extrovert configurations. 

## Movements

Several movements are implemented. For the movements to work, they need to be installed using Choregraph in the Nao robot.

Authors:
```bash
Victor Retamal
Chantal Voges
Quinn Scott
Mohammed Majeed
Fauve Wevers
Demi Peek
