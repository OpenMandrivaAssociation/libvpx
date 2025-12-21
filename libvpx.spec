%define git 0
%define major 11
%define libname %mklibname vpx
%define devname %mklibname -d vpx

%global optflags %{optflags} -O3 -pthread

Summary:	VP8/9 Video Codec SDK
Name:		libvpx
Version:	1.15.2
Release:	1
License:	BSD
Group:		System/Libraries
Url:		https://www.webmproject.org/tools/vp8-sdk/
Source0:	https://github.com/webmproject/libvpx/archive/v%{version}/%{name}-%{version}.tar.gz
%ifarch %{ix86} %{x86_64}
# (Configure script uses `which` to locate yasm and nasm, so
# while it looks odd, it's indeed an x86-only dependency)
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool-base
BuildRequires:	slibtool
BuildRequires:	make
BuildRequires:	which
BuildRequires:	yasm
%endif

%description
libvpx provides the VP8 and VP9 SDK, which allows you to integrate your
applications with the VP8/VP9 video codec, a high quality, royalty
free, open source codec deployed on millions of computers and devices
worldwide.

%package -n %{libname}
Summary:	VP8 Video Codec SDK
Group:		System/Libraries

%description -n %{libname}
libvpx provides the VP8/9 SDK, which allows you to integrate your applications
with the VP8/9 video codec, a high quality, royalty free, open source codec
deployed on millions of computers and devices worldwide.

%package -n %{devname}
Summary:	Development files for libvpx
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n %{devname}
Development libraries and headers for developing software against
libvpx.

%package utils
Summary:	VP8/VP9 utilities and tools
Group:		Video

%description utils
A selection of utilities and tools for VP8/VP9, including a sample encoder
and decoder.

%prep
%autosetup -p1

sed -i 's/armv7\*-hardfloat*/armv7hl-/g' build/make/configure.sh
sed -i 's/armv7\*/armv7l-*/g' build/make/configure.sh

%build
%set_build_flags

%ifarch %{ix86}
%global vpxtarget x86-linux-gcc
%else
%ifarch %{x86_64}
%global vpxtarget x86_64-linux-gcc
%else
%ifarch %{aarch64}
%global vpxtarget arm64-linux-gcc
%else
%ifarch %{arm}
%global vpxtarget armv7-linux-gcc
sed -i 's/arm-none-linux-gnueabi/%{_host}/g'  build/make/configure.sh
%else
%global vpxtarget generic-gnu
%endif
%endif
%endif
%endif

./configure \
    --enable-shared \
    --enable-vp8 \
    --enable-vp9 \
    --enable-vp9-highbitdepth \
    --enable-postproc \
    --enable-runtime-cpu-detect \
    --target="%{vpxtarget}" \
    --enable-multithread \
    --enable-experimental \
    --disable-static \
    --extra-cflags="-U_FORTIFY_SOURCE %{optflags} -O3" \
    --extra-cxxflags="-U_FORTIFY_SOURCE %{optflags} -O3" \
    --enable-pic \
    --disable-install-srcs

# stupid config
sed -i -e "s|/usr/local|%{_prefix}|g" config.mk
sed -i -e "s|^LIBSUBDIR=lib|LIBSUBDIR=%{_lib}|g" config.mk

%make_build

%install
%make_install DIST_DIR=%{buildroot}%{_prefix}

install -m0755 examples/simple_decoder %{buildroot}%{_bindir}/vp8_simple_decoder
install -m0755 examples/simple_encoder %{buildroot}%{_bindir}/vp8_simple_encoder
install -m0755 examples/twopass_encoder %{buildroot}%{_bindir}/vp8_twopass_encoder
install -m0755 examples/vpx_temporal_svc_encoder %{buildroot}%{_bindir}/vpx_temporal_svc_encoder
install -m0755 examples/vp9_lossless_encoder %{buildroot}%{_bindir}/vp9_lossless_encoder
rm -rf %{buildroot}/%{_defaultdocdir}/html

%files -n %{libname}
%{_libdir}/libvpx.so.%{major}*

%files -n %{devname}
%doc AUTHORS CHANGELOG LICENSE README
%{_includedir}/vpx/
%{_libdir}/pkgconfig/vpx.pc
%{_libdir}/libvpx.so

%files utils
%{_bindir}/*
