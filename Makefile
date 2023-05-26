# Note: This makefile is largely copied from the sample Makefile provided in my own Python-Docker
# project (https://github.com/jusjayson/Python-Docker) in order to allow for containerization without
# exceeding the given time limit.

ifdef DOCKER_COMMON_ENV_PATH
include $(DOCKER_COMMON_ENV_PATH)
endif

ifdef DOCKER_SPECIFIC_ENV_PATH
include $(DOCKER_SPECIFIC_ENV_PATH)
endif

export

NAMESPACE ?=
PYTHON_VERSION ?= 3.10

DOCKER_APP_DEST ?= /app
DOCKER_CTX_FROM_COMPOSE ?= ../../..
DOCKER_CTX_FROM_PROJECT_ROOT ?= .
DOCKER_CTX_FROM_PYTHON_DOCKER ?=..
DOCKER_ENTRYPOINT_DEST ?= /entrypoint.sh
DOCKER_LOCAL_CMD ?= /bin/bash
DOCKER_PROJECT_ROOT_FROM_CTX ?= .
DOCKER_PROJECT_NAME ?= collx
DOCKER_PROJECT_SERVICE_NAME ?= collx-interview
DOCKER_PYTHON_DOCKER_FROM_CTX ?= Python-Docker
DOCKER_REGISTRY ?= fake-registry-10fbaaa7-a475-4bc2-822c-b10d749e66a1.com
DOCKER_TAG_VERSION ?= latest

DOCKER_APP_SOURCE_FROM_COMPOSE ?= $(DOCKER_CTX_FROM_COMPOSE)/$(DOCKER_PROJECT_ROOT_FROM_CTX)
DOCKER_COMPOSE_FILE ?= $(DOCKER_CTX_FROM_PYTHON_DOCKER)/$(DOCKER_PROJECT_ROOT_FROM_CTX)/config/docker/compose/docker-compose.$(NAMESPACE).yaml
DOCKER_CONFIG_FOLDER_PATH ?= /root/.collx/config
DOCKER_LOG_FOLDER_PATH ?= /root/.collx/logs
DOCKER_USER_CONFIG_PATH_FROM_CTX ?= $(DOCKER_PROJECT_ROOT_FROM_CTX)/config
DOCKER_USER_LOCAL_LOG_PATH_FROM_CTX ?= $(DOCKER_PROJECT_ROOT_FROM_CTX)/logs


# Docker
build-base-image:
	cd $(DOCKER_CTX_FROM_PROJECT_ROOT)/$(DOCKER_PYTHON_DOCKER_FROM_CTX); \
		DOCKER_REGISTRY=$(DOCKER_REGISTRY) \
		DOCKER_TAG_VERSION=$(DOCKER_TAG_VERSION) \
		PYTHON_VERSION=$(PYTHON_VERSION) \
		make build-base-image

build-project:
	cd $(DOCKER_CTX_FROM_PROJECT_ROOT)/$(DOCKER_PYTHON_DOCKER_FROM_CTX); \
		DOCKER_APP_DEST=$(DOCKER_APP_DEST) \
		DOCKER_CONFIG_FOLDER_PATH=$(DOCKER_CONFIG_FOLDER_PATH) \
		DOCKER_CTX_FROM_PYTHON_DOCKER=$(DOCKER_CTX_FROM_PYTHON_DOCKER) \
		DOCKER_ENTRYPOINT_DEST=$(DOCKER_ENTRYPOINT_DEST) \
		DOCKER_ENTRYPOINT_SOURCE_FROM_CTX=$(DOCKER_ENTRYPOINT_SOURCE_FROM_CTX) \
		DOCKER_LOG_FOLDER_PATH=$(DOCKER_LOG_FOLDER_PATH) \
		DOCKER_PROJECT_ROOT_FROM_CTX=$(DOCKER_PROJECT_ROOT_FROM_CTX) \
		DOCKER_REGISTRY=$(DOCKER_REGISTRY) \
		DOCKER_TAG_VERSION=$(DOCKER_TAG_VERSION) \
		DOCKER_USER_CONFIG_PATH_FROM_CTX=$(DOCKER_USER_CONFIG_PATH_FROM_CTX) \
		NAMESPACE=$(NAMESPACE) \
		PROJECT_NAME=$(DOCKER_PROJECT_NAME) \
		DONT_PASS_SSH_KEYS=true \
		make build-project

build-test-project: export NAMESPACE=test
build-test-project: export DOCKER_ENTRYPOINT_SOURCE_FROM_CTX=$(DOCKER_PROJECT_ROOT_FROM_CTX)/config/docker/scripts/test-entrypoint.sh
build-test-project:
	make build-project;

launch-test-project: export NAMESPACE=test
launch-test-project:
	DOCKER_APP_DEST=${DOCKER_APP_DEST} \
	DOCKER_APP_SOURCE_FROM_COMPOSE=$(DOCKER_APP_SOURCE_FROM_COMPOSE) \
	DOCKER_CONFIG_FOLDER_PATH=$(DOCKER_CONFIG_FOLDER_PATH) \
	DOCKER_CTX_FROM_COMPOSE=$(DOCKER_CTX_FROM_COMPOSE) \
	DOCKER_LOG_FOLDER_PATH=$(DOCKER_LOG_FOLDER_PATH) \
	DOCKER_REGISTRY=$(DOCKER_REGISTRY) \
	DOCKER_TAG_VERSION=$(DOCKER_TAG_VERSION) \
	DOCKER_USER_CONFIG_PATH_FROM_CTX=${DOCKER_USER_CONFIG_PATH_FROM_CTX} \
	DOCKER_USER_LOCAL_LOG_PATH_FROM_CTX=${DOCKER_USER_LOCAL_LOG_PATH_FROM_CTX} \
	NAMESPACE=$(NAMESPACE) \
	PROJECT_NAME=$(DOCKER_PROJECT_NAME) \
	docker compose \
		-f config/docker/compose/docker-compose.test.yaml \
		run -it ${DOCKER_PROJECT_SERVICE_NAME} $(DOCKER_LOCAL_CMD)

init-project:
	cd $(DOCKER_CTX_FROM_PROJECT_ROOT)/$(DOCKER_PYTHON_DOCKER_FROM_CTX) && \
		DOCKER_ABSOLUTE_APP_SOURCE=$(shell realpath ".") \
		DOCKER_REGISTRY=$(DOCKER_REGISTRY) \
		DOCKER_TAG_VERSION=$(DOCKER_TAG_VERSION) \
		PYTHON_VERSION=$(PYTHON_VERSION) \
		make init-project

load-db:  # XXX: getting issues including sql file in scripts
	docker exec -it compose-collx-mysql-1 /bin/bash -c "mysql -uroot -pim_not_safe_change_me collx_prod < collx_card_data.sql"

teardown-project:
	cd $(DOCKER_CTX_FROM_PROJECT_ROOT)/$(DOCKER_PYTHON_DOCKER_FROM_CTX); \
		DOCKER_COMPOSE_FILE=$(DOCKER_COMPOSE_FILE) \
		PROJECT_NAME=taxer \
		make teardown-project

teardown-test-project: export DOCKER_COMPOSE_FILE=$(DOCKER_CTX_FROM_PYTHON_DOCKER)/$(DOCKER_PROJECT_ROOT_FROM_CTX)/config/docker/compose/docker-compose.test.yaml
teardown-test-project: export NAMESPACE=test
teardown-test-project:
	make teardown-project

run-tests: export DOCKER_LOCAL_CMD=pytest
run-tests:
	make launch-test-project

test-matching-accuracy: export DOCKER_LOCAL_CMD=python test.py test_accuracy
test-matching-accuracy:
	make launch-test-project

match-cards: export DOCKER_LOCAL_CMD=python test.py match_cards
match-cards:
	make launch-test-project