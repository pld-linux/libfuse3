Summary:	Filesystem in Userspace
Summary(pl.UTF-8):	System plików w przestrzeni użytkownika
Name:		libfuse3
Version:	3.10.4
Release:	1
License:	LGPL v2 (library), GPL v2 (tools)
Group:		Applications/System
#Source0Download: https://github.com/libfuse/libfuse/releases
Source0:	https://github.com/libfuse/libfuse/releases/download/fuse-%{version}/fuse-%{version}.tar.xz
# Source0-md5:	55b87e9ed691c2fa698e491241985b4a
Patch0:		%{name}-build.patch
URL:		https://github.com/libfuse/libfuse
BuildRequires:	meson >= 0.42
BuildRequires:	ninja >= 1.5
BuildRequires:	rpmbuild(macros) >= 1.736
BuildRequires:	sed >= 4.0
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
FUSE (Filesystem in Userspace) is a simple interface for userspace
programs to export a virtual filesystem to the Linux kernel. FUSE also
aims to provide a secure method for non privileged users to create and
mount their own filesystem implementations.

This package contains a shared library.

%description -l pl.UTF-8
FUSE stanowi prosty interfejs dla programów działających w przestrzeni
użytkownika eksportujący wirtualny system plików do jądra Linuksa.
FUSE ma również na celu udostępnienie bezpiecznej metody tworzenia i
montowania własnych implementacji systemów plików przez zwykłych
(nieuprzywilejowanych) użytkowników.

Ten pakiet zawiera bibliotekę współdzieloną.

%package devel
Summary:	Filesystem in Userspace - Development header files
Summary(pl.UTF-8):	System plików w przestrzeni użytkownika - pliki nagłówkowe
License:	LGPL v2
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Libfuse3 library header files.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki libfuse3.

%package static
Summary:	Filesystem in Userspace - static library
Summary(pl.UTF-8):	System plików w przestrzeni użytkownika - biblioteka statyczna
License:	LGPL v2
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static libfuse3 library.

%description static -l pl.UTF-8
Statyczna biblioteka libfuse3.

%package apidocs
Summary:	API documentation for FUSE 3 library
Summary(pl.UTF-8):	Dokumentacja API biblioteki FUSE 3
Group:		Documentation

%description apidocs
API documentation for FUSE 3 library.

%description apidocs -l pl.UTF-8
Dokumentacja API biblioteki FUSE 3.

%package -n libfuse-common
Summary:	Common package for FUSE 2 and FUSE 3
Summary(pl.UTF-8):	Pliki wspólne dla FUSE 2 i FUSE 3
Group:		Libraries
Conflicts:	libfuse < 2.9.7-3
Conflicts:	libfuse3 < 3.2.4-2

%description -n libfuse-common
Common package for FUSE 2 and FUSE 3.

%description -n libfuse-common -l pl.UTF-8
Pliki wspólne dla FUSE 2 i FUSE 3.

%package tools
Summary:	Tools to mount FUSE 3 based filesystems
Summary(pl.UTF-8):	Narzędzia do montowania systemów plików opartych na FUSE 3
License:	GPL v2
Group:		Applications/System
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires:	%{name} = %{version}-%{release}
Requires:	libfuse-common = %{version}-%{release}
Requires:	mount >= 2.18
Provides:	group(fuse)

%description tools
Tools to mount FUSE 3 based filesystems.

%description tools -l pl.UTF-8
Narzędzia do montowania systemów plików opartych na FUSE 3.

%prep
%setup -q -n fuse-%{version}
%patch0 -p1

%{__sed} -i '/FUSERMOUNT_PROG/s,fusermount3,%{_bindir}/fusermount3,' lib/mount.c

# gold is missing base versioning
install -d ld-dir
[ ! -x /usr/bin/ld.bfd ] || ln -sf /usr/bin/ld.bfd ld-dir/ld

%build
PATH=$(pwd)/ld-dir:$PATH

%meson build \
	-Duseroot=false

%ninja_build -C build

%{?with_tests:%ninja_test -C build}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/%{_lib},%{_sysconfdir},/sbin}

%ninja_install -C build

%{__mv} $RPM_BUILD_ROOT%{_libdir}/libfuse3.so.* $RPM_BUILD_ROOT/%{_lib}
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libfuse3.so
ln -sf /%{_lib}/$(basename $RPM_BUILD_ROOT/%{_lib}/libfuse3.so.*.*) \
	$RPM_BUILD_ROOT%{_libdir}/libfuse3.so

%{__mv} $RPM_BUILD_ROOT{%{_sbindir},/sbin}/mount.fuse3

# part of default udev rules nowdays
%{__rm} $RPM_BUILD_ROOT/lib/udev/rules.d/99-fuse3.rules

# not needed
%{__rm} $RPM_BUILD_ROOT/etc/init.d/fuse3

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%pre tools
%groupadd -g 84 fuse

%files
%defattr(644,root,root,755)
%doc README.md ChangeLog.rst AUTHORS doc/{README.NFS,fast17-vangoor.pdf,kernel.txt}
%attr(755,root,root) /%{_lib}/libfuse3.so.*.*.*
%attr(755,root,root) %ghost /%{_lib}/libfuse3.so.3

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libfuse3.so
%{_includedir}/fuse3
%{_pkgconfigdir}/fuse3.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/libfuse3.a

%files apidocs
%defattr(644,root,root,755)
%doc doc/html/*

%files -n libfuse-common
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/fuse.conf

%files tools
%defattr(644,root,root,755)
%attr(4755,root,root) %{_bindir}/fusermount3
%attr(755,root,root) /sbin/mount.fuse3
%{_mandir}/man1/fusermount3.1*
%{_mandir}/man8/mount.fuse3.8*
