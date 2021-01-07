echo "install docker"
curl -sSL get.docker.com | sh
systemctl start docker.service
systemctl enable docker.service

echo "docker调优"
echo "关闭selinux"
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config

echo "修改时区为上海"
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

echo "修改系统语言环境"
echo 'LANG="en_US.UTF-8"' >> /etc/profile;source /etc/profile

echo "同步时间"
yum install -y ntp
ntpdate pool.ntp.org
systemctl enable ntpd

echo "kernel性能调优:"
echo "1、修复可能出现的网络问题"
echo "2、修改最大进程数"
sudo cat >> /etc/sysctl.conf<<EOF
net.ipv4.ip_forward=1
net.bridge.bridge-nf-call-iptables=1
net.ipv4.neigh.default.gc_thresh1=4096
net.ipv4.neigh.default.gc_thresh2=6144
net.ipv4.neigh.default.gc_thresh3=8192
kernel.pid_max=1000000
EOF
systemctl restart network
sysctl -p

echo "关闭防火墙"
firewall-cmd --state
systemctl stop firewalld.service
systemctl disable firewalld.service

echo "设置docker加速器"
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
   "registry-mirrors": [
       "https://mirror.ccs.tencentyun.com"
  ]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker