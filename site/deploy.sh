#!/bin/bash
# 一键部署课程站点到 pcb.xiaxianlin.com (43.250.173.13)
# 用法: ./deploy.sh   （在 site/ 目录执行）
# 注：本网络对 SSH 大文件传输不稳定，采用 300KB 分块上传 + 服务器重组
set -e
cd "$(dirname "$0")"
HOST=root@43.250.173.13
DIR=/var/www/pcb-course
SSH="ssh -o BatchMode=yes -o ConnectTimeout=8"

echo "① 构建最新站点..."
python3 build.py >/dev/null

echo "② 打包分块上传..."
COPYFILE_DISABLE=1 tar czf /tmp/pcb-site.tar.gz --exclude '._*' index.html fonts assets sim
rm -f /tmp/pcbpart-*
split -b 300k /tmp/pcb-site.tar.gz /tmp/pcbpart-
$SSH "$HOST" 'rm -rf /tmp/up && mkdir -p /tmp/up'
for f in /tmp/pcbpart-*; do
  b=$(basename "$f"); ok=0
  for i in 1 2 3 4 5; do
    scp -q -o BatchMode=yes -o IPQoS=none -o ConnectTimeout=8 "$f" "$HOST:/tmp/up/$b" 2>/dev/null && ok=1 && break
    sleep 2
  done
  [ $ok = 1 ] || { echo "✗ $b 上传失败"; exit 1; }
done

echo "③ 服务器重组部署..."
$SSH "$HOST" "
set -e
cat /tmp/up/pcbpart-* > /tmp/pcb-site.tar.gz
tar xzf /tmp/pcb-site.tar.gz -C $DIR 2>/dev/null || true
find $DIR -name '._*' -delete
chown -R www-data:www-data $DIR
nginx -t >/dev/null 2>&1 && systemctl reload nginx
rm -rf /tmp/up
"

echo "④ 验证..."
sleep 1
code=$(curl -s -o /dev/null -w "%{http_code}" -m 10 https://pcb.xiaxianlin.com/)
echo "https://pcb.xiaxianlin.com -> HTTP $code ✅"
