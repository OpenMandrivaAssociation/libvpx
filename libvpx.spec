%define git 0
%define major 7
%define libname %mklibname vpx %{major}
%define devname %mklibname -d vpx

%global optflags %{optflags} -O3 -pthread

Summary:	VP8/9 Video Codec SDK
Name:		libvpx
Version:	1.11.0
Release:	1
License:	BSD
Group:		System/Libraries
Url:		http://www.webmproject.org/tools/vp8-sdk/
Source0:	https://github.com/webmproject/libvpx/archive/v%{version}/%{name}-%{version}.tar.gz
BuildRequires:	glibc-devel

%ifarch %{ix86} %{x86_64}
BuildRequires:	yasm
%endif

%description
libvpx provides the VP8 and VP9 SDK, which allows you to integrate your
applications with the VP8/VP9 video codec, a high quality, royalty
free, open source codec deployed on millions of computers and devices
worldwide.

%package -n	%{libname}
Summary:	VP8 Video Codec SDK
Group:		System/Libraries

%description -n %{libname}
libvpx provides the VP8/9 SDK, which allows you to integrate your applications
with the VP8/9 video codec, a high quality, royalty free, open source codec
deployed on millions of computers and devices worldwide.

%package -n	%{devname}
Summary:	Development files for libvpx
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n	%{devname}
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
export CC=clang
export CXX=clang++
%set_build_flags

%ifarch %{ix86}
%global vpxtarget x86-linux-gcc
%else
%ifarch %{x86_64}
%global vpxtarget x86_64-linux-gcc
%else
%global vpxtarget generic-gnu
%endif
%ifarch %{arm}
%global vpxtarget armv7-linux-gcc
sed -i 's/arm-none-linux-gnueabi/%{_host}/g'  build/make/configure.sh
%endif
%endif

./configure \
    --enable-shared \
    --enable-vp8 \
    --enable-vp9 \
    --enable-postproc \
    --enable-runtime-cpu-detect \
    --target=%{vpxtarget} \
    --enable-experimental \
    --enable-vp9-highbitdepth \
    --disable-static \
    --extra-cflags="-U_FORTIFY_SOURCE %{optflags} -O3" \
	--extra-cxxflags="-U_FORTIFY_SOURCE %{optflags} -O3" \
    --enable-pic \
    --disable-install-srcs

# stupid config
perl -pi -e "s|/usr/local|%{_prefix}|g" config.mk
perl -pi -e "s|^LIBSUBDIR=lib|LIBSUBDIR=%{_lib}|g" config.mk

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
