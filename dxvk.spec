# We can't extract debuginfo from Windows binaries
%undefine _debugsource_packages

Name:		dxvk
Version:	3.0.2
Release:        1
Summary:	Vulkan-based D3D11 implementation for Linux / Wine
License:	zlib-acknowledgement
Group:		System/Emulators/PC
URL:		https://github.com/doitsujin/dxvk
# GitHub archives omit git submodules. Pin the dxbc-spirv commit used by v3.0.2.
%define dxbc_spirv_commit 887bb6c4c4af01a9ccb757e92d35fca3896794f6
Source0:	https://github.com/doitsujin/dxvk/archive/v%{version}.tar.gz
Source1:	https://gitlab.freedesktop.org/frog/libdisplay-info/-/archive/windows/libdisplay-info-windows.tar.bz2
Source2:	https://github.com/doitsujin/dxbc-spirv/archive/%{dxbc_spirv_commit}/dxbc-spirv-%{dxbc_spirv_commit}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  glslang-devel
BuildRequires:  meson
BuildRequires:  ninja
BuildRequires:  pkgconfig
BuildRequires:  (wine or proton or proton-experimental or proton-bleeding-edge)
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
# Required if the 32-bit DLL is used, thankfully 32-bit is getting rare
Recommends:     libSDL2-2.0.so.0

BuildArch:	noarch

Provides:	direct3d-implementation
Requires:	(wine or proton or proton-experimental or proton-bleeding-edge)
Supplements:	wine
Supplements:	proton
Supplements:	proton-experimental

%patchlist
dxvk-3.0.2-win32-threads.patch

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
rmdir dxbc-spirv
tar xf %{S:2}
mv dxbc-spirv-* dxbc-spirv
# dxbc-spirv hardcodes a nested SPIRV-Headers submodule path
mkdir -p dxbc-spirv/submodules/spirv_headers/include
cp -a %{_includedir}/spirv dxbc-spirv/submodules/spirv_headers/include

%conf
mkdir ../build
meson setup \
    --cross-file build-win64.txt \
    --strip \
    --buildtype "release" \
    --unity off \
    --wrap-mode nodownload \
    --prefix /%{name} \
    ../build

mkdir ../build32
meson setup \
    --cross-file build-win32.txt \
    --strip \
    --buildtype "release" \
    --unity off \
    --wrap-mode nodownload \
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
