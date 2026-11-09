#!/bin/bash
# PCB 课程站点本地服务管理脚本
# 用法: ./service.sh {start|stop|restart|status|uninstall}
LABEL="com.pcbcourse.site"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
PORT=8420
URL="http://127.0.0.1:${PORT}"
UID_=$(id -u)

loaded() { launchctl print "gui/${UID_}/${LABEL}" >/dev/null 2>&1; }

case "$1" in
  start)
    if loaded; then
      launchctl kickstart "gui/${UID_}/${LABEL}" && echo "服务已在运行，已重启进程"
    else
      launchctl bootstrap "gui/${UID_}" "$PLIST" && launchctl kickstart "gui/${UID_}/${LABEL}"
      echo "服务已启动: $URL"
    fi
    ;;
  stop)
    launchctl bootout "gui/${UID_}/${LABEL}" 2>/dev/null && echo "服务已停止" || echo "服务未在运行"
    ;;
  restart)
    loaded && launchctl kickstart -k "gui/${UID_}/${LABEL}" && echo "已重启: $URL" || echo "服务未加载，请先 ./service.sh start"
    ;;
  status)
    if loaded; then
      echo "launchd: 已加载 (KeepAlive 开机自启)"
      code=$(curl -s -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null)
      [ "$code" = "200" ] && echo "HTTP: $URL -> 200 OK" || echo "HTTP: $URL 无响应 ($code)"
    else
      echo "launchd: 未加载"
    fi
    ;;
  uninstall)
    launchctl bootout "gui/${UID_}/${LABEL}" 2>/dev/null
    rm -f "$PLIST" && echo "已停止服务并删除 $PLIST"
    ;;
  *)
    echo "用法: $0 {start|stop|restart|status|uninstall}"
    echo "服务地址: $URL (仅本机访问)"
    exit 1
    ;;
esac
