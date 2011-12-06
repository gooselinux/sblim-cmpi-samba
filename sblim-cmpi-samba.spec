%define provider_dir %{_libdir}/cmpi
%define tog_pegasus_version 2:2.5.1

Name:           sblim-cmpi-samba
Version:        1.0
Release:        1%{?dist}
Summary:        SBLIM WBEM-SMT Samba

Group:          Applications/System
License:        EPL
URL:            http://sblim.wiki.sourceforge.net/
Source0:        http://downloads.sourceforge.net/sblim/%{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Patch0:         sblim-cmpi-samba-0.2.3-model.patch
Patch1:         sblim-cmpi-samba-0.5.2-include.patch

BuildRequires:  tog-pegasus-devel >= %{tog_pegasus_version}
BuildRequires:  sblim-tools-libra-devel
BuildRequires:  sblim-cmpi-devel
BuildRequires:  dos2unix
Requires:       sblim-tools-libra
Requires:       tog-pegasus >= %{tog_pegasus_version}
Requires:       samba >= 3.0.10
Requires:       /etc/ld.so.conf.d
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
Provides:       cmpi-samba = %{version}

%description
The cmpi-samba package provides access to the samba configuration data
via CIMOM technology/infrastructure.
It contains the Samba CIM Model, CMPI Provider with the Samba task specific
Resource Access.

%package devel
Summary:        SBLIM WBEM-SMT Samba - Header Development Files
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       tog-pegasus

%description devel
SBLIM WBEM-SMT Samba Development Package contains header files and
link libraries for dependent provider packages

%package test
Summary:        SBLIM WBEM-SMT Samba - Testcase Files
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}
Requires:       sblim-testsuite
Requires:       tog-pegasus

%description test
SBLIM WBEM-SMT Samba Provider Testcase Files for the SBLIM Testsuite

%prep
%setup -q
%patch0 -p0 -b .model
%patch1 -p1 -b .include

%build
%ifarch s390 s390x ppc ppc64
export CFLAGS="$RPM_OPT_FLAGS -fsigned-char"
%else
export CFLAGS="$RPM_OPT_FLAGS" 
%endif
%configure \
   TESTSUITEDIR=%{_datadir}/sblim-testsuite \
   CIMSERVER=pegasus \
   PROVIDERDIR=%{provider_dir}
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
# remove unused libtool files
rm -f $RPM_BUILD_ROOT/%{_libdir}/*a
rm -f $RPM_BUILD_ROOT/%{_libdir}/cmpi/*a
# shared libraries
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d
echo "%{_libdir}/cmpi" > $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d/sblim-cmpi-samba-%{_arch}.conf
dos2unix $RPM_BUILD_ROOT/%{_datadir}/%{name}/smt_smb_ra_test.py

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,0755)
%doc %{_datadir}/doc/%{name}-%{version}
%doc %{_mandir}/man5/smt_smb_ra_support.conf.5.gz
%{_datadir}/sblim-cmpi-samba
%{_libdir}/libRaToolsSmb.so.*
%{_libdir}/libLinux_SmbGeneralProviderBasic.so.*
%{_libdir}/libIBM_SmbProviderTooling.so.*
%config(noreplace) %{_sysconfdir}/smt_smb*.conf
%{_libdir}/cmpi/libcmpiLinux_Samba*.so
%{_libdir}/cmpi/libcmpiSambaCIM_ConcreteJob.so
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf

%files devel
%defattr(-,root,root,0755)
%{_includedir}/sblim/smt_smb*.h
%{_libdir}/libRaToolsSmb.so
%{_libdir}/libLinux_SmbGeneralProviderBasic.so
%{_libdir}/libIBM_SmbProviderTooling.so

%files test
%defattr(-,root,root,0755)
%{_datadir}/sblim-testsuite/system/linux/Linux_Samba*
%{_datadir}/sblim-testsuite/cim/Linux_Samba*
%{_datadir}/sblim-testsuite/xml/Linux_Samba*
%{_datadir}/sblim-testsuite/smbpasswd
%{_datadir}/sblim-testsuite/smbusers
%{_datadir}/sblim-testsuite/smb.conf
%{_datadir}/sblim-testsuite/test-cmpi-samba.sh
%{_datadir}/sblim-testsuite/test-cmpi-samba-associations.pl

# Conditional definition of schema and registration files
%define SAMBA_SCHEMA %{_datadir}/%{name}/Linux_Samba.mof
%define SAMBA_REGISTRATION %{_datadir}/%{name}/Linux_Samba.registration

%pre
# If upgrading, deregister old version
if [ $1 -gt 1 ]; then
  %{_datadir}/%{name}/provider-register.sh -d \
  -t pegasus -r %{SAMBA_REGISTRATION} -m %{SAMBA_SCHEMA} > /dev/null 2>&1 || :;
fi

%post
/sbin/ldconfig
if [ $1 -ge 1 ]; then
# Register Schema and Provider - this is higly provider specific
%{_datadir}/%{name}/provider-register.sh \
  -t pegasus -r %{SAMBA_REGISTRATION} -m %{SAMBA_SCHEMA} > /dev/null 2>&1 || :;
fi;

%preun
# Deregister only if not upgrading 
if [ $1 -eq 0 ]; then
  %{_datadir}/%{name}/provider-register.sh -d \
  -t pegasus -r %{SAMBA_REGISTRATION} -m %{SAMBA_SCHEMA} > /dev/null 2>&1 || :;
fi

%postun
# Run ldconfig only if not upgrading
if [ $1 -eq 0 ]; then
  /sbin/ldconfig
fi

%changelog
* Wed Jun 30 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.0-1
- Update to sblim-cmpi-samba-1.0

* Thu Oct 22 2009 Vitezslav Crhonek <vcrhonek@redhat.com> - 0.5.2-2
- Update "include" patch
- Remove *.pyc and *.pyo exclude from files

* Thu Oct 15 2009 Vitezslav Crhonek <vcrhonek@redhat.com> - 0.5.2-1
- Initial support
