# We can't extract debuginfo from Windows binaries
%undefine _debugsource_packages

Name:		dxvk
Version:	2.6.2
Release:        1
Summary:	Vulkan-based D3D11 implementation for Linux / Wine
License:	zlib-acknowledgement
Group:		System/Emulators/PC
URL:		https://github.com/doitsujin/dxvk
Source0:	https://github.com/doitsujin/dxvk/archive/v%{version}.tar.gz
Source1:	https://gitlab.freedesktop.org/frog/libdisplay-info/-/archive/windows/libdisplay-info-windows.tar.bz2

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  glslang-devel
BuildRequires:  meson
BuildRequires:  ninja
BuildRequires:  pkgconfig
BuildRequires:  (wine or proton or proton-experimental)
BuildRequires:  xz
BuildRequires:  pkgconfig(glfw3)
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(sdl2)
BuildRequires:	vulkan-headers
BuildRequires:	spirv-headers
BuildRequires:	glslang

BuildRequires:	cross-x86_64-w64-mingw32-binutils
BuildRequires:	cross-x86_64-w64-mingw32-gcc
BuildRequires:	cross-x86_64-w64-mingw32-libc
BuildRequires:  cross-i686-w64-mingw32-binutils
BuildRequires:  cross-i686-w64-mingw32-gcc
BuildRequires:  cross-i686-w64-mingw32-libc

# Loaded at runtime
Requires:       libSDL2-2.0.so.0()(64bit)
Requires:       libSDL2-2.0.so.0

BuildArch:	noarch

Provides:	direct3d-implementation
Requires:	(wine or proton or proton-experimental)
Supplements:	wine
Supplements:	proton
Supplements:	proton-experimental

%patchlist

%description
Provides a Vulkan-based implementation of DXGI and D3D11 in order to run 3D applications on Linux using Wine

%prep
%autosetup -p1
# eat up your libdisplay-info!
sed -i '/library=static/d' meson.build

# Upstream, vulkan-headers and spirv-headers are pulled in as
# git submodules. Let's copy in system headers to make sure the
# versions match
mkdir -p include/vulkan/include
cp -a %{_includedir}/vulkan %{_includedir}/vk_video include/vulkan/include
mkdir -p include/spirv/include
cp -a %{_includedir}/spirv include/spirv/include
# We can skip mingw-directx-headers because our mingw has them - so system
# headers will be found
cd subprojects
rmdir libdisplay-info
tar xf %{S:1}
mv libdisplay-info-* libdisplay-info

%conf
mkdir ../build
meson setup \
    --cross-file build-win64.txt \
    --strip \
    --buildtype "release" \
    --unity off \
    --prefix /%{name} \
    ../build

mkdir ../build32
meson setup \
    --cross-file build-win32.txt \
    --strip \
    --buildtype "release" \
    --unity off \
    --prefix /%{name} \
    ../build32

%build
%ninja_build -C ../build
%ninja_build -C ../build32

%install
install -vD -m 0644 dxvk.conf %{buildroot}%{_sysconfdir}/dxvk.conf

mkdir -p %{buildroot}%{_libdir}/wine/x86_64-windows/
mv ../build/src/*/*.dll %{buildroot}%{_libdir}/wine/x86_64-windows/

mkdir -p %{buildroot}%{_prefix}/lib/wine/i386-windows/
mv ../build32/src/*/*.dll %{buildroot}%{_prefix}/lib/wine/i386-windows/

%files
%defattr(-,root,root)
%doc README.md
%license LICENSE
%config %{_sysconfdir}/dxvk.conf
%{_libdir}/wine/x86_64-windows/*.dll
%{_prefix}/lib/wine/i386-windows/*.dll
