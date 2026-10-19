# ---- Stage 1: Build ----
FROM golang:1.21-alpine@sha256:8ee9b9e11ef79e314a7584040451a6df8e72a66712e741bf75951e05e587404e AS builder


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
FROM gcr.io/distroless/static-debian12:nonroot@sha256:52dcfbabb7457ea47c82f6e13af8c8a4a1d9f7b0145142b3ecab20f2b888411d

COPY --from=builder /chaos-worker /chaos-worker

# nonroot user (65532) is provided by distroless:nonroot
USER nonroot

EXPOSE 8080

ENTRYPOINT ["/chaos-worker"]
