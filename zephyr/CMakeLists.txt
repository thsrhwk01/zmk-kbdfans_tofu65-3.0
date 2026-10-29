if(CONFIG_TOFU65_UNICORE)
  zephyr_library()
  zephyr_library_include_directories(${APPLICATION_SOURCE_DIR}/include ../src)
  zephyr_library_sources(
    ../src/kscan_unicore.c
    ../src/platform_init.c
    ../src/behavior_unicore_bootloader.c
  )
  zephyr_library_sources_ifdef(CONFIG_ZMK_HID_INDICATORS
    ../src/caps_indicator.c
    ../src/unicore_rgb_byte.S
  )
endif()

