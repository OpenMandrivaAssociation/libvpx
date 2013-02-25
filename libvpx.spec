%define	major	1
%define	libname	%mklibname vpx %{major}
%define	devname	%mklibname -d vpx

Name:		libvpx
Summary:	VP8 Video Codec SDK
Version:	1.1.0
Release:	2
License:	BSD
Group:		System/Libraries
URL:		http://www.webmproject.org/tools/vp8-sdk/
Source0:	http://webm.googlecode.com/files/%{name}-v%{version}.tar.bz2
%ifarch %{ix86} x86_64
BuildRequires:	yasm
%endif
BuildRequires:	doxygen php-cli

%description
libvpx provides the VP8 SDK, which allows you to integrate your applications 
with the VP8 video codec, a high quality, royalty free, open source codec 
deployed on millions of computers and devices worldwide. 

%package -n	%{libname}
Summary:	VP8 Video Codec SDK
Group:		System/Libraries

%description -n %{libname}
libvpx provides the VP8 SDK, which allows you to integrate your applications 
with the VP8 video codec, a high quality, royalty free, open source codec 
deployed on millions of computers and devices worldwide. 

%package -n	%{devname}
Summary:	Development files for libvpx
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n	%{devname}
Development libraries and headers for developing software against 
libvpx.

%package	utils
Summary:	VP8 utilities and tools
Group:		Video

%description	utils
A selection of utilities and tools for VP8, including a sample encoder
and decoder.

%prep
%setup -q -n %{name}-v%{version}

%build
%ifarch %{ix86}
%global vpxtarget x86-linux-gcc
%else
%ifarch	x86_64
%global	vpxtarget x86_64-linux-gcc
%else
%global vpxtarget generic-gnu
%endif
%ifarch %{arm}
%global vpxtarget armv7-linux-gcc
sed -i 's/arm-none-linux-gnueabi/armv7l-mandriva-linux-gnueabi/g'  build/make/configure.sh
%endif
%endif
%setup_compile_flags

./configure \
    --enable-shared \
    --disable-static \
    --target=%{vpxtarget} \
    --enable-pic \
    --disable-install-srcs

# stupid config
perl -pi -e "s|/usr/local|%{_prefix}|g" config.mk
perl -pi -e "s|^LIBSUBDIR=lib|LIBSUBDIR=%{_lib}|g" config.mk

%make verbose=true target=libs
%make verbose=true target=examples
%make verbose=true target=docs

%install

make DIST_DIR=%{buildroot}%{_prefix} install

install -m0755 simple_decoder %{buildroot}%{_bindir}/vp8_simple_decoder
install -m0755 simple_encoder %{buildroot}%{_bindir}/vp8_simple_encoder
install -m0755 twopass_encoder %{buildroot}%{_bindir}/vp8_twopass_encoder

%files -n %{libname}
%doc AUTHORS CHANGELOG LICENSE README
%{_libdir}/libvpx.so.%{major}*

%files -n %{devname}
# These are SDK docs, not really useful to an end-user.
%doc docs/html
%{_includedir}/vpx/
%{_libdir}/pkgconfig/vpx.pc
%{_libdir}/libvpx.so

%files utils
%{_bindir}/*
