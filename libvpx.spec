%define major 0
%define libname %mklibname vpx %major
%define develname %mklibname -d vpx
%define snapshot 0
Name:			libvpx
Summary:		VP8 Video Codec SDK
Version:		0.9.5
Release:		%mkrel 2
License:		BSD
Group:			System/Libraries
Source0:		http://webm.googlecode.com/files/%{name}-v%{version}.tar.bz2
Source1:		libvpx.pc
# Thanks to debian.
Source2:		libvpx.ver
Patch0:			libvpx-0.9.0-no-explicit-dep-on-static-lib.patch
URL:			http://www.webmproject.org/tools/vp8-sdk/
BuildRoot: %{_tmppath}/%{name}-%{version}-buildroot
%ifarch %{ix86} x86_64
BuildRequires:		yasm
%endif
BuildRequires:		doxygen, php-cli

%description
libvpx provides the VP8 SDK, which allows you to integrate your applications 
with the VP8 video codec, a high quality, royalty free, open source codec 
deployed on millions of computers and devices worldwide. 

%package -n %libname
Summary:		VP8 Video Codec SDK
Group:			System/Libraries

%description -n %libname
libvpx provides the VP8 SDK, which allows you to integrate your applications 
with the VP8 video codec, a high quality, royalty free, open source codec 
deployed on millions of computers and devices worldwide. 



%package -n %develname
Summary:		Development files for libvpx
Group:			Development/C
Requires:		%{libname} = %{version}-%{release}
Provides: %name-devel = %version-%release

%description -n %develname
Development libraries and headers for developing software against 
libvpx.

%package utils
Summary:		VP8 utilities and tools
Group:			Video
Requires:		%{libname} = %{version}-%{release}

%description utils
A selection of utilities and tools for VP8, including a sample encoder
and decoder.

%prep
%setup -q -n %name-v%version
%patch0 -p1 -b .no-static-lib

%build
%ifarch %{ix86}
%global vpxtarget x86-linux-gcc
%else
%ifarch	x86_64
%global	vpxtarget x86_64-linux-gcc
%else
%global vpxtarget generic-gnu
%endif
%endif

./configure --target=%{vpxtarget} --enable-pic --disable-install-srcs

# Hack our optflags in.
sed -i "s|\"vpx_config.h\"|\"vpx_config.h\" %{optflags} -fPIC|g" libs-%{vpxtarget}.mk
sed -i "s|\"vpx_config.h\"|\"vpx_config.h\" %{optflags} -fPIC|g" examples-%{vpxtarget}.mk
sed -i "s|\"vpx_config.h\"|\"vpx_config.h\" %{optflags} -fPIC|g" docs-%{vpxtarget}.mk

%make verbose=true target=libs

# Really? You couldn't make this a shared library? Ugh.
# Oh well, I'll do it for you.
mkdir tmp
cd tmp
ar x ../libvpx_g.a
cd ..
gcc -fPIC -shared -pthread -lm -Wl,--no-undefined -Wl,-soname,libvpx.so.0 -Wl,--version-script,%{SOURCE2} -Wl,-z,noexecstack -o libvpx.so.0.0.0 tmp/*.o 
rm -rf tmp

# Temporarily dance the static libs out of the way
mv libvpx.a libNOTvpx.a
mv libvpx_g.a libNOTvpx_g.a

# We need to do this so the examples can link against it.
ln -sf libvpx.so.0.0.0 libvpx.so

%make verbose=true target=examples
%make verbose=true target=docs

# Put them back so the install doesn't fail
mv libNOTvpx.a libvpx.a
mv libNOTvpx_g.a libvpx_g.a

%install
rm -rf %buildroot
make DIST_DIR=%{buildroot}%{_prefix} install

cp simple_decoder %buildroot%_bindir/vp8_simple_decoder                        
cp simple_encoder %buildroot%_bindir/vp8_simple_encoder                        
cp twopass_encoder %buildroot%_bindir/vp8_twopass_encoder            

# Install the pkg-config file
mkdir -p %{buildroot}%{_libdir}/pkgconfig/
install -m0644 %{SOURCE1} %{buildroot}%{_libdir}/pkgconfig/
# Fill in the variables
sed -i "s|@PREFIX@|%{_prefix}|g" %{buildroot}%{_libdir}/pkgconfig/libvpx.pc
sed -i "s|@LIBDIR@|%{_libdir}|g" %{buildroot}%{_libdir}/pkgconfig/libvpx.pc
sed -i "s|@INCLUDEDIR@|%{_includedir}|g" %{buildroot}%{_libdir}/pkgconfig/libvpx.pc

mkdir -p %{buildroot}%{_includedir}/vpx/
install -p libvpx.so.0.0.0 %{buildroot}%{_libdir}
pushd %{buildroot}%{_libdir}
ln -sf libvpx.so.0.0.0 libvpx.so
ln -sf libvpx.so.0.0.0 libvpx.so.0
ln -sf libvpx.so.0.0.0 libvpx.so.0.0
popd
pushd %{buildroot}
# Stuff we don't need.
rm -rf usr/build/ usr/md5sums.txt usr/lib*/*.a usr/CHANGELOG usr/README
# Fix the binary permissions
chmod 755 usr/bin/*
popd

%clean
rm -rf %{buildroot}

%files -n %libname
%defattr(-,root,root,-)
%doc AUTHORS CHANGELOG LICENSE README
%{_libdir}/libvpx.so.%{major}*

%files -n %develname
%defattr(-,root,root,-)
# These are SDK docs, not really useful to an end-user.
%doc docs/html
%{_includedir}/vpx/
%{_libdir}/pkgconfig/libvpx.pc
%{_libdir}/libvpx.so

%files utils
%defattr(-,root,root,-)
%{_bindir}/*

