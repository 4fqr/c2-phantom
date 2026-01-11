# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /build

# Install build dependencies
RUN apk add --no-cache git gcc musl-dev

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=1 GOOS=linux go build -a -installsuffix cgo -ldflags="-s -w" -o c2-server main.go

# Final stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates tzdata

WORKDIR /app

# Copy binary from builder
COPY --from=builder /build/c2-server .

# Create non-root user
RUN addgroup -g 1000 phantom && \
    adduser -D -u 1000 -G phantom phantom && \
    chown -R phantom:phantom /app

USER phantom

EXPOSE 8080 443

ENTRYPOINT ["./c2-server"]
