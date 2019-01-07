%{?scl:%scl_package gperftools}
%{!?scl:%global pkg_name %{name}}

# This package used to be called "google-perftools", but it was renamed on 2012-02-03.

%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

Name:		%{?scl_prefix}gperftools
Version:	2.6.1
Release:	1.bs1%{?dist}
License:	BSD
Group:		Development/Tools
Summary:	Very fast malloc and performance analysis tools
URL:		http://code.google.com/p/gperftools/
Source0:	https://googledrive.com/host/0B6NtGsLhIcf7MWxMMF9JdTN3UVk/%{pkg_name}-%{version}.tar.gz


Requires:	%{?scl_prefix}gperftools-devel = %{version}-%{release}

# we don't want to require or provide any pkgconfig(xxx) symbols
%global __pkgconfig_requires ""
%global __pkgconfig_provides ""


%description
Perf Tools is a collection of performance analysis tools, including a 
high-performance multi-threaded malloc() implementation that works
particularly well with threads and STL, a thread-friendly heap-checker,
a heap profiler, and a cpu-profiler.

This is a metapackage which pulls in all of the gperftools (and pprof)
binaries, libraries, and development headers, so that you can use them.


%package devel
Summary:	Development libraries and headers for gperftools
Group:		Development/Libraries
Requires:	%{?scl_prefix}%{pkg_name}-libs%{?_isa} = %{version}-%{release}
Provides:	%{?scl_prefix}google-perftools-devel = %{version}-%{release}
Obsoletes:	%{?scl_prefix}google-perftools-devel < 2.0


%description devel
Libraries and headers for developing applications that use gperftools.


%package libs
Summary:	Libraries provided by gperftools
Provides:	%{?scl_prefix}google-perftools-libs = %{version}-%{release}
Obsoletes:	%{?scl_prefix}google-perftools-libs < 2.0
%{?scl:Requires: %{scl}-runtime}


%description libs
Libraries provided by gperftools, including libtcmalloc and libprofiler.


%prep
%{?scl:scl enable %{scl} - << \EOF}
set -e
%setup -n %{pkg_name}-%{version} -q


# Fix end-of-line encoding
sed -i 's/\r//' README_windows.txt

# No need to have exec permissions on source code
chmod -x src/*.h src/*.cc

# make libtool able to handle soname in format sclname-1
sed -i -r 's|(major=\.)(\$func_arith_result)|\1$verstring_prefix\2|' ltmain.sh

%{?scl:EOF}


%build
%{?scl_prefix:export verstring_prefix="%{scl_prefix}"}
%{?scl:scl enable %{scl} - << \EOF}
set -e
CFLAGS=`echo $RPM_OPT_FLAGS -fno-strict-aliasing -Wno-unused-local-typedefs -DTCMALLOC_LARGE_PAGES | sed -e 's|-fexceptions||g'`
CXXFLAGS=`echo $RPM_OPT_FLAGS -fno-strict-aliasing -Wno-unused-local-typedefs -DTCMALLOC_LARGE_PAGES | sed -e 's|-fexceptions||g'`
%configure --disable-static --disable-libunwind

# Bad rpath!
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
# Can't build with smp_mflags
make 
%{?scl:EOF}


%install
%{?scl_prefix:export verstring_prefix="%{scl_prefix}"}
%{?scl:scl enable %{scl} - << \EOF}
set -e
make DESTDIR=%{buildroot} docdir=%{_pkgdocdir}/ install
find %{buildroot} -type f -name "*.la" -exec rm -f {} ';'

# Delete useless files
rm -rf %{buildroot}%{_pkgdocdir}/INSTALL
# NO pprof for mongodb SCL
rm %{buildroot}%{_bindir}/pprof
rm -f %{buildroot}%{_mandir}/man1/*
%{?scl:EOF}


%check
%{?scl:scl enable %{scl} - << \EOF}
set -e
# http://code.google.com/p/google-perftools/issues/detail?id=153
%ifnarch ppc
# Their test suite is almost always broken.
# LD_LIBRARY_PATH=./.libs make check
%endif
%{?scl:EOF}


%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig


%files


%files devel
%{_pkgdocdir}/
%{_includedir}/google/
%{_includedir}/gperftools/
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc


%files libs
%{_libdir}/*.so.*


%changelog
* Thu Oct 12 2017 Miroslav Rezanina <mrezanin@redhat.com> - 2.4-8.el7
- Rebase to 2.6.1 [bz#1431240]
- Removed libunwind usage [bz#1467203]
- Resolves: bz#1431240 
  (gperftools fails to build on s390x, lacks s390x support)
- Resolves: bz#1467203
  (Please, remove libunwind from the gperftools-libs (and 389-ds-base) requirements)

* Wed Jun 22 2016 Miroslav Rezanina <mrezanin@redhat.com> - 2.4-8.el7
- gp-Use-initial-exec-tls-for-libunwind-s-recursion-flag.patch [bz#1339710]
- Resolves: bz#1339710
  (initalization of 'recursive' tls variable in libunwind stack capturer occasionally triggers deadlock in ceph)

* Wed Aug 26 2015 Miroslav Rezanina <mrezanin@redhat.com> 2.4-7
- Rebuild to fix NVR [bz#1269032]
- Resolves: bz#1269032
  (gperftools NVR lower than EPEL version)

* Wed Aug 26 2015 Miroslav Rezanina <mrezanin@redhat.com> 2.4-2
- gperf-allow-customizing-trace-filename.patch [bz#1232702]
- Resolves: bz#1232702
  (gperftools: tcmalloc debug version uses hard-coded path /tmp/google.alloc) 

* Tue Jun 02 2015 Miroslav Rezanina <mrezanin@redhat.com> 2.4-1
- Import to RHEL
