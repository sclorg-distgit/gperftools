%{?scl:%scl_package gperftools}
%{!?scl:%global pkg_name %{name}}

# This package used to be called "google-perftools", but it was renamed on 2012-02-03.

%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

Name:		%{?scl_prefix}gperftools
Version:	2.5
Release:	4%{?dist}
License:	BSD
Group:		Development/Tools
Summary:	Very fast malloc and performance analysis tools
URL:		https://github.com/gperftools/gperftools
Source0:	https://github.com/gperftools/gperftools/releases/download/%{pkg_name}-%{version}/%{pkg_name}-%{version}.tar.gz
ExcludeArch:	s390

%ifnarch s390x
BuildRequires:	%{?scl_prefix}libunwind-devel
%endif
Requires:	%{?scl_prefix}gperftools-devel = %{version}-%{release}
%if 0%{!?scl:1}
Requires:	%{?scl_prefix}pprof = %{version}-%{release}
%endif

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

%if 0%{!?scl:1}
%package -n %{?scl_prefix}pprof
Summary:	CPU and Heap Profiler tool
Requires:	gv, graphviz
BuildArch:	noarch
Provides:	%{?scl_prefix}google-perftools = %{version}-%{release}
Obsoletes:	%{?scl_prefix}google-perftools < 2.0
%{?scl:Requires: %{scl}-runtime}


%description -n %{?scl_prefix}pprof
Pprof is a heap and CPU profiler tool, part of the gperftools suite.
%endif

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
%configure --disable-static

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
%if 0%{?scl:1}
rm %{buildroot}%{_bindir}/pprof
rm -f %{buildroot}%{_mandir}/man1/*
%endif

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

%if 0%{!?scl:1}
%files -n %{?scl_prefix}pprof
%{_bindir}/pprof
%{_mandir}/man1/*
%endif


%files devel
%{_pkgdocdir}/
%{_includedir}/google/
%{_includedir}/gperftools/
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc


%files libs
%{_libdir}/*.so.*


%changelog
* Fri Jun 23 2017 Marek Skalický <mskalick@redhat.com> - 2.5-4
- Remove pprof dependency

* Thu Jun 15 2017 Marek Skalický <mskalick@redhat.com> - 2.5-3
- Rebase to gperftools 2.5 from Fedora 25 and convert it to SCL

* Thu Apr 28 2016 Peter Robinson <pbrobinson@fedoraproject.org> 2.5-2
- Power64 has libunwind now

* Tue Apr 26 2016 Tom Callaway <spot@fedoraproject.org> - 2.5-1
- update to 2.5

* Tue Mar  8 2016 Tom Callaway <spot@fedoraproject.org> - 2.4.91-1
- update to 2.4.91
- re-enable hardened builds (upstream disabled dynamic sized delete by default)

* Fri Mar 04 2016 Than Ngo <than@redhat.com> - 2.4.90-3
- Disable hardened build on ppc64/ppc64le (RHBZ#1314483).

* Mon Feb 29 2016 Richard W.M. Jones <rjones@redhat.com> - 2.4.90-2
- Disable hardened build on 32 bit ARM (RHBZ#1312462).

* Mon Feb 22 2016 Tom Callaway <spot@fedoraproject.org> - 2.4.90-1
- update to 2.4.90

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.4-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jun  9 2015 Tom Callaway <spot@fedoraproject.org> - 2.4-4
- fix modern futex handling (thanks to Paolo Bonzini)

* Mon Jun  1 2015 Tom Callaway <spot@fedoraproject.org> - 2.4-3
- enable futex for ARM

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 2.4-2
- Rebuilt for GCC 5 C++11 ABI change

* Fri Mar 27 2015 Tom Callaway <spot@fedoraproject.org> 2.4-1
- update to 2.4

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jul 10 2014 Dan Horák <dan[at]danny.cz> -  2.2.1-1
- Update to new upstream 2.2.1 release
- Fixes build on ppc arches

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Jun  4 2014 Peter Robinson <pbrobinson@fedoraproject.org> 2.2-1
- Update to new upstream 2.2 release
- Add support for new arches (aarch64, ppc64le, mips)

* Tue May 13 2014 Jaromir Capik <jcapik@redhat.com> - 2.1-5
- Replacing ppc64 with the power64 macro (#1077632)

* Sat Jan  4 2014 Tom Callaway <spot@fedoraproject.org> - 2.1-4
- re-enable FORTIFY_SOURCE

* Fri Dec  6 2013 Ville Skyttä <ville.skytta@iki.fi> - 2.1-3
- Install docs to %%{_pkgdocdir} where available (#993798), include NEWS.
- Fix bogus date in %%changelog.

* Sat Aug 03 2013 Petr Pisar <ppisar@redhat.com> - 2.1-2
- Perl 5.18 rebuild

* Wed Jul 31 2013 Tom Callaway <spot@fedoraproject.org> - 2.1-1
- update to 2.1 (fixes arm)
- disable -fexceptions, as that breaks things on el6, possibly arm

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 2.0-12
- Perl 5.18 rebuild

* Tue Jun  4 2013 Tom Callaway <spot@fedoraproject.org> - 2.0-11
- pass -fno-strict-aliasing
- create "gperftools" metapackage.
- update to svn r218 (cleanups, some ARM fixes)

* Thu Mar 14 2013 Dan Horák <dan[at]danny.cz> - 2.0-10
- build on ppc64 as well

* Fri Mar  1 2013 Tom Callaway <spot@fedoraproject.org> - 2.0-9
- update to svn r190 (because google can't make releases)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Aug  3 2012 Tom Callaway <spot@fedoraproject.org> - 2.0-7
- fix compile with glibc 2.16

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Feb 20 2012 Peter Robinson <pbrobinson@fedoraproject.org> - 2.0-5
- Enable ARM as a supported arch

* Thu Feb 16 2012 Tom Callaway <spot@fedoraproject.org> - 2.0-4
- fix bug in -devel Requires

* Tue Feb 14 2012 Tom Callaway <spot@fedoraproject.org> - 2.0-3
- pprof doesn't actually need gperftools-libs

* Tue Feb 14 2012 Tom Callaway <spot@fedoraproject.org> - 2.0-2
- rework package so that pprof is a noarch subpackage, while still
  enforcing the ExclusiveArch for the libs

* Tue Feb 14 2012 Tom Callaway <spot@fedoraproject.org> - 2.0-1
- rename to gperftools
- update to 2.0

* Wed Jan  4 2012 Tom Callaway <spot@fedoraproject.org> - 1.9.1-1
- update to 1.9.1

* Mon Oct 24 2011 Tom Callaway <spot@fedoraproject.org> - 1.8.3-3
- split libraries out into subpackage to minimize dependencies

* Wed Sep 21 2011 Remi Collet <remi@fedoraproject.org> - 1.8.3-2
- rebuild for new libunwind

* Tue Aug 30 2011 Tom Callaway <spot@fedoraproject.org> - 1.8.3-1
- update to 1.8.3

* Mon Aug 22 2011 Tom Callaway <spot@fedoraproject.org> - 1.8.2-1
- update to 1.8.2

* Thu Jul 28 2011 Tom Callaway <spot@fedoraproject.org> - 1.8.1-1
- update to 1.8.1

* Mon Jul 18 2011 Tom Callaway <spot@fedoraproject.org> - 1.8-1
- update to 1.8

* Wed Jun 29 2011 Tom Callaway <spot@fedoraproject.org> - 1.7-4
- fix tcmalloc compile against current glibc, fix derived from:
  http://src.chromium.org/viewvc/chrome?view=rev&revision=89800

* Thu May 12 2011 Tom Callaway <spot@fedoraproject.org> - 1.7-3
- add Requires: graphviz, gv for pprof

* Fri Mar 11 2011 Dan Horák <dan[at]danny.cz> - 1.7-2
- switch to ExclusiveArch

* Fri Feb 18 2011 Tom Callaway <spot@fedoraproject.org> - 1.7-1
- update to 1.7

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Dec  2 2010 Tom "spot" Callaway <tcallawa@redhat.com> - 1.6-2
- fix pprof to work properly with jemalloc (bz 657118)

* Fri Aug  6 2010 Tom "spot" Callaway <tcallawa@redhat.com> - 1.6-1
- update to 1.6

* Wed Jan 20 2010 Tom "spot" Callaway <tcallawa@redhat.com> - 1.5-1
- update to 1.5
- disable broken test suite

* Sat Sep 12 2009 Tom "spot" Callaway <tcallawa@redhat.com> - 1.4-1
- update to 1.4

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul  2 2009 Tom "spot" Callaway <tcallawa@redhat.com> - 1.3-2
- disable tests for ppc, upstream ticket #153

* Thu Jul  2 2009 Tom "spot" Callaway <tcallawa@redhat.com> - 1.3-1
- update to 1.3

* Wed May 20 2009 Tom "spot" Callaway <tcallawa@redhat.com> - 1.2-1
- update to 1.2

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.99.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Sep 22 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0.99.1-1
- update to 0.99.1
- previous patches in 0.98-1 were taken upstream

* Mon Aug 25 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0.98-1
- update to 0.98
- fix linuxthreads.c compile (upstream issue 74)
- fix ppc compile (upstream issue 75)
- enable ppc

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.95-4
- Autorebuild for GCC 4.3

* Tue Feb 19 2008 Tom "spot" Callaway <tcallawa@redhat.com> 0.95-3
- re-disable ppc/ppc64

* Tue Feb 19 2008 Tom "spot" Callaway <tcallawa@redhat.com> 0.95-2
- ppc/ppc64 doesn't have libunwind

* Tue Feb 19 2008 Tom "spot" Callaway <tcallawa@redhat.com> 0.95-1
- 0.95 (all patches taken upstream)
- enable ppc support
- workaround broken ptrace header (no typedef for u32)

* Fri Jan  4 2008 Tom "spot" Callaway <tcallawa@redhat.com> 0.94.1-1
- bump to 0.94.1
- fix for gcc4.3
- fix unittest link issue

* Thu Aug 23 2007 Tom "spot" Callaway <tcallawa@redhat.com> 0.93-1
- upstream merged my patch!
- rebuild for BuildID

* Wed Aug  1 2007 Tom "spot" Callaway <tcallawa@redhat.com> 0.92-1
- bump to 0.92

* Thu May 17 2007 Tom "spot" Callaway <tcallawa@redhat.com> 0.91-3.1
- excludearch ppc64

* Sun Apr 29 2007 Tom "spot" Callaway <tcallawa@redhat.com> 0.91-3
- The tests work fine for me locally, but some of them fail inside mock.

* Sun Apr 29 2007 Tom "spot" Callaway <tcallawa@redhat.com> 0.91-2
- no support for ppc yet

* Mon Apr 23 2007 Tom "spot" Callaway <tcallawa@redhat.com> 0.91-1
- alright, lets see if this works now.

* Wed Oct 12 2005 Tom "spot" Callaway <tcallawa@redhat.com> 0.3-2
- change group to Development/Tools

* Mon Oct 10 2005 Tom "spot" Callaway <tcallawa@redhat.com> 0.3-1
- initial package for Fedora Extras
