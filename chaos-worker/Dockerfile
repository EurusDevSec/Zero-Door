# ---- Stage 1: Build ----
FROM golang:1.21-alpine AS builder

# git required for go module downloads
RUN apk add --no-cache git

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

# Pure Go build (segmentio/kafka-go requires no CGO)
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-s -w" \
    -o /chaos-worker \
    ./cmd/

# ---- Stage 2: Runtime ----
# Distroless for minimal attack surface
FROM gcr.io/distroless/static-debian12:nonroot

COPY --from=builder /chaos-worker /chaos-worker

# nonroot user (65532) is provided by distroless:nonroot
USER nonroot

EXPOSE 8080

ENTRYPOINT ["/chaos-worker"]
