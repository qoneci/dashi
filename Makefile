NAME = dashi
.PHONY: build fullbuild default

default: build

build:
	docker build -t $(NAME) --rm=true --no-cache=true .

fullbuild:
	docker build -t $(NAME) --rm=true --no-cache=true -f Dockerfile-fullbuild .
