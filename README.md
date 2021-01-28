# TJTS5901

[![pipeline status](https://gitlab.jyu.fi/startuplab/courses/tjts5901-continuous-software-engineering/beemaptemplate/badges/master/pipeline.svg)](https://gitlab.jyu.fi/startuplab/courses/tjts5901-continuous-software-engineering/beemaptemplate/-/commits/master) 
[![coverage report](https://gitlab.jyu.fi/startuplab/courses/tjts5901-continuous-software-engineering/beemaptemplate/badges/master/coverage.svg)](https://gitlab.jyu.fi/startuplab/courses/tjts5901-continuous-software-engineering/beemaptemplate/-/commits/master)

https://agile-team-299406.ew.r.appspot.com/

This repository was created to be an example for the course work.

Python 3.8.5

to run app locally in docker

`$ docker build -t beemaptemplate .`

`$ docker run -p 5000:5000 beemaptemplate:latest`


## How to run pre-commit locally

pre-commit will also modify the files. Modifications need to be commited separately

`pip install pre-commit`

`pre-commit install`

`pre-commit run --all-files`
