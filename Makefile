.PHONY: all
all: build-base build-red

.PHONY: build-base
build-base:
	python -m build --sdist
	python -m build --sdist "--config-setting=--build-option=--project-version-override=1.0.1"

.PHONY: build-red
build-red:
	python -m build --sdist \
		"--config-setting=--build-option=--project-name-override=$$(head -1 red-build-config.txt)" \
		"--config-setting=--build-option=--pkg-build-error-msg=$$(tail +3 red-build-config.txt)"
	python -m build --sdist "--config-setting=--build-option=--project-version-override=1.0.1" \
		"--config-setting=--build-option=--project-name-override=$$(head -1 red-build-config.txt)" \
		"--config-setting=--build-option=--pkg-build-error-msg=$$(tail +3 red-build-config.txt)"
