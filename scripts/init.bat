
pushd c:\temp
  del kicad_libs/*
  rmdir kicad_libs
  git clone --depth 1 git://smisioto.eu/kicad_libs.git

  