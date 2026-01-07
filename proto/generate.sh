#!/bin/bash
# Generate protobuf code for Python and Go

# Python
python -m grpc_tools.protoc \
    -I. \
    --python_out=../c2_phantom/proto \
    --grpc_python_out=../c2_phantom/proto \
    c2.proto

# Go
protoc \
    -I. \
    --go_out=../server/proto \
    --go-grpc_out=../server/proto \
    c2.proto

echo "✓ Protobuf code generated for Python and Go"
