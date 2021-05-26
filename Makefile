IMAGE := pulp
TAG := latest

default: help
help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo "  help           to show this message"
	@echo "  build          to build container image"
	@echo "  push           to push container image"

build:
	ansible-playbook ./.ci/assets/ansible/build_container.yaml -e "{\"pulp_images\": [{\"name\": \"${IMAGE}\", \"tag\": \"${TAG}\"}]}"

push:
	ansible-playbook ./.ci/assets/ansible/push_container.yaml -e "{\"pulp_images\": [{\"name\": \"${IMAGE}\", \"tag\": \"${TAG}\"}]}"

.PHONY: help build push
