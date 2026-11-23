#!/usr/bin/env bash
# start.sh / stop.sh for the oversight gateway (Agent Computer VM or sandbox)
cd "$(dirname "$0")"
PIDF=gateway.pid
case "$1" in
  start)
    [ -f "$PIDF" ] && kill -0 "$(cat $PIDF)" 2>/dev/null && { echo "already running ($PIDF)"; exit 0; }
    nohup python3 -m uvicorn oversight:app --host 0.0.0.0 --port "${PORT:-3000}" --log-level warning > gateway.log 2>&1 < /dev/null &
    echo $! > "$PIDF"
    sleep 2
    curl -s -m 5 "localhost:${PORT:-3000}/health" > /dev/null && echo "gateway up on :${PORT:-3000}" || { echo "FAILED — see gateway.log"; tail -20 gateway.log; exit 1; }
    ;;
  stop)
    [ -f "$PIDF" ] && kill "$(cat $PIDF)" 2>/dev/null && rm -f "$PIDF" && echo stopped
    ;;
  status)
    [ -f "$PIDF" ] && kill -0 "$(cat $PIDF)" 2>/dev/null && echo running || echo down
    ;;
esac
