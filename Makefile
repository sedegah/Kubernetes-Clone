.PHONY: help build-go build-python test-go test-python run-demo-go run-demo-python clean install-python

help:
	@echo "Kubernetes Clone - Simplified Commands"
	@echo ""
	@echo "Go Commands:"
	@echo "  make build-go        - Build Go binary"
	@echo "  make run-demo-go     - Run Go demo"
	@echo "  make test-go         - Test Go implementation"
	@echo ""
	@echo "Python Commands:"
	@echo "  make install-python  - Install Python dependencies"
	@echo "  make run-demo-python - Run Python demo"
	@echo "  make test-python     - Test Python implementation"
	@echo ""
	@echo "Combined Commands:"
	@echo "  make build           - Build both Go and Python"
	@echo "  make test            - Test both implementations"
	@echo "  make demo            - Run both demos"
	@echo "  make clean           - Clean build artifacts"

# Go targets
build-go:
	@echo "Building Go binary..."
	cd go && go build -o ../kclone ./cmd/kclone
	@echo "✓ Built kclone binary"

run-demo-go:
	@echo "Running Go demo..."
	cd go && go run ./cmd/demo

test-go:
	@echo "Testing Go implementation..."
	cd go && go test -v ./...

# Python targets
install-python:
	@echo "Installing Python dependencies..."
	cd python && pip install -e .
	@echo "✓ Python package installed"

run-demo-python:
	@echo "Running Python demo..."
	cd python && python -m kclone.__main__

test-python:
	@echo "Testing Python implementation..."
	cd python && pytest -v

# Combined targets
build: build-go
	@echo "✓ Build complete"

test: test-go test-python
	@echo "✓ All tests passed"

demo: run-demo-go
	@echo ""
	@echo "Python Demo:"
	@echo "============"
	@$(MAKE) run-demo-python

clean:
	@echo "Cleaning build artifacts..."
	rm -f kclone
	rm -rf go/kclone
	rm -rf python/src/kclone/__pycache__
	rm -rf python/tests/__pycache__
	rm -rf python/src/kclone.egg-info
	@echo "✓ Clean complete"

# Quick commands
go: build-go
	./kclone --help

python: install-python
	kclone --help


clean:
	rm -f kclone

help:
	@echo "Available commands:"
	@echo "  make build  - Build the kclone binary"
	@echo "  make run    - Build and show help"
	@echo "  make demo   - Run the demo"
	@echo "  make clean  - Remove built binary"
