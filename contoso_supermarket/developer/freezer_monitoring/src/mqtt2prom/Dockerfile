FROM golang:1.20 as builder

# install busybox so there is a shell and we can use the following for debugging
# kubectl exec -it $pod -- /bin/busybox sh
RUN apt-get update && apt-get install -y busybox

COPY . /build/mqtt2prometheus
WORKDIR /build/mqtt2prometheus
RUN make static_build TARGET_FILE=/bin/mqtt2prometheus

FROM gcr.io/distroless/static-debian10:nonroot
WORKDIR /
COPY --from=builder /bin/mqtt2prometheus /mqtt2prometheus
ENTRYPOINT ["/mqtt2prometheus"]
