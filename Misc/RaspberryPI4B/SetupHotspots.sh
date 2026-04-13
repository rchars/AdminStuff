#!/usr/bin/env bash

for x in {0..1}
do
  nmcli device wifi hotspot ifname wlan$x ssid Hotspot0 password SECRET_PASSWORD_$x con-name Hotspot$x
  nmcli conn modify Hotspot$x connection.autoconnect yes
  nmcli conn modify Hotspot$x connection.autoconnect-priority "$((998 - $x))"
  nmcli conn modify Hotspot$x connection.lldp 0
  nmcli conn modify Hotspot$x connection.llmnr 0
  nmcli conn modify Hotspot$x connection.mdns 0

  nmcli conn modify Hotspot$x 802-11-wireless.ap-isolation 1
  nmcli conn modify Hotspot$x 802-11-wireless.cloned-mac-address permanent
  nmcli conn modify Hotspot$x 802-11-wireless.mac-address-randomization 1

  nmcli conn modify Hotspot$x 802-11-wireless-security.key-mgmt wpa-psk

  nmcli conn modify Hotspot$x ipv4.addresses 10.42.$x.1/24
  nmcli conn modify Hotspot$x ipv4.method manual
  nmcli conn modify Hotspot$x ipv4.may-fail false
  nmcli conn modify Hotspot$x ipv4.dhcp-ipv6-only-preferred 0

  nmcli conn modify Hotspot$x ipv6.method disabled
done
