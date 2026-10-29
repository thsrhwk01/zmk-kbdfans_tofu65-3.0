if(CONFIG_TOFU65_UNICORE)
  zephyr_library()
  zephyr_library_include_directories(${APPLICATION_SOURCE_DIR}/include ../src)
  zephyr_library_sources(
    ../src/kscan_unicore.c
    ../src/platform_init.c
    ../src/behavior_unicore_bootloader.c
  )
endif()

