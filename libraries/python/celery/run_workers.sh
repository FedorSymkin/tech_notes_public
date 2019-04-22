#!/bin/bash

setsid celery worker -A tasks --concurrency=10 &