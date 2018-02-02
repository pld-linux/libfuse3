Summary:	Filesystem in Userspace
Summary(pl.UTF-8):	System plików w przestrzeni użytkownika
Name:		libfuse3
Version:	3.2.1
Release:	1
License:	GPL v2
Group:		Applications/System
#Source0Download: https://github.com/libfuse/libfuse/releases
Source0:	https://github.com/libfuse/libfuse/releases/download/fuse-%{version}/fuse-%{version}.tar.xz
# Source0-md5:	5dc79e3b7e0afbd6f8c5c335405227d1
Source1:	fuse.conf
Patch0:		%{name}-build.patch
URL:		https://github.com/libfuse/libfuse
BuildRequires:	meson
BuildRequires:	sed >= 4.0
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Suggests:	mount >= 2.18
Provides:	group(fuse)
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
Summary:	Filesytem in Userspace - Development header files
Summary(pl.UTF-8):	System plików w przestrzeni użytkownika - pliki nagłówkowe
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Libfuse library header files.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki libfuse.

%prep
%setup -q -n fuse-%{version}
%patch0 -p1

sed -i '/FUSERMOUNT_PROG/s,fusermount3,%{_bindir}/fusermount3,' lib/mount.c

# gold is missing base versioning
install -d ld-dir
[ ! -x /usr/bin/ld.bfd ] || ln -sf /usr/bin/ld.bfd ld-dir/ld

%build
PATH=$(pwd)/ld-dir:$PATH

%meson build

%meson_build -C build

%{?with_tests:%meson_test -C build}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/%{_lib},%{_sysconfdir},/sbin}

%meson_install -C build

mv -f $RPM_BUILD_ROOT%{_libdir}/libfuse3.so.* $RPM_BUILD_ROOT/%{_lib}
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libfuse3.so
ln -sf /%{_lib}/$(cd $RPM_BUILD_ROOT/%{_lib}; echo libfuse3.so.*.*) \
	$RPM_BUILD_ROOT%{_libdir}/libfuse3.so

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}

mv $RPM_BUILD_ROOT{%{_sbindir},/sbin}/mount.fuse3
mv $RPM_BUILD_ROOT%{_mandir}/man8/mount.fuse{,3}.8.gz

# part of default udev rules nowdays
rm $RPM_BUILD_ROOT/lib/udev/rules.d/99-fuse3.rules

# not needed
rm $RPM_BUILD_ROOT/etc/init.d/fuse3

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 84 fuse

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README.md ChangeLog.rst AUTHORS doc/*
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/fuse.conf
%attr(4755,root,root) %{_bindir}/fusermount3
%attr(755,root,root) /sbin/mount.fuse3
%attr(755,root,root) /%{_lib}/libfuse3.so.*.*.*
%attr(755,root,root) %ghost /%{_lib}/libfuse3.so.3
%{_mandir}/man1/fusermount3.1*
%{_mandir}/man8/mount.fuse3.8*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libfuse3.so
%{_includedir}/fuse3
%{_pkgconfigdir}/fuse3.pc
