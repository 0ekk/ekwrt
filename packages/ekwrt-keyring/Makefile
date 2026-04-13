include $(TOPDIR)/rules.mk

PKG_NAME:=ekwrt-keyring
PKG_RELEASE:=1

include $(INCLUDE_DIR)/package.mk

define Package/ekwrt-keyring
  SECTION:=base
  CATEGORY:=Base system
  TITLE:=ekwrt package signing keyring
  PKGARCH:=all
endef

define Package/ekwrt-keyring/description
 Installs local package signing public keys for ekwrt repositories.
endef

Build/Prepare=
Build/Configure=
Build/Compile=

ifneq ($(CONFIG_USE_APK),)
define Package/ekwrt-keyring/install
	$(INSTALL_DIR) $(1)/etc/apk/keys
	$(INSTALL_DATA) $(BUILD_KEY_APK_PUB) $(1)/etc/apk/keys/
endef
else
define Package/ekwrt-keyring/install
	$(INSTALL_DIR) $(1)/etc/opkg/keys
	$(CP) $(BUILD_KEY).pub $(1)/etc/opkg/keys/`$(STAGING_DIR_HOST)/bin/usign -F -p $(BUILD_KEY).pub`
endef
endif

$(eval $(call BuildPackage,ekwrt-keyring))
