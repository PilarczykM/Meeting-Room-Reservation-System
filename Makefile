# Makefile for Meeting-Room-Reservation-System

.PHONY: help install test lint format all

help:
	@echo "Commands:"
	@echo "  install    : Install dependencies"
	@echo "  test       : Run tests"
	@echo "  lint       : Run linter"
	@echo "  format     : Run formatter"
	@echo "  all        : Run lint, format, and test"

install:
	uv sync

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

all: lint format test
