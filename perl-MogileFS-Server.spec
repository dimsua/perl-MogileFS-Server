Name:       perl-MogileFS-Server
Version:    2.73
Release:    3%{?dist}
Summary:    Server part of the MogileFS distributed filesystem
License:    GPL+ or Artistic
Group:      System Environment/Daemons
URL:        https://github.com/mogilefs/MogileFS-Server
Source0:    https://github.com/mogilefs/MogileFS-Server/archive/%{version}.tar.gz
Source2:    mogilefsd.init
Source3:    mogilefsd.conf
Source4:    mogilefs.conf
Patch0:	    mogilefsd_remove_mogstored.patch
Patch1:	    replication-policy-create-open.patch
Patch2:	    mogilefs_crash_fix.patch
Patch3:	    audit.patch

BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:  noarch

BuildRequires:  perl(ExtUtils::MakeMaker)
BuildRequires:  perl(Test::More)
BuildRequires:  perl-MogileFS-Client
BuildRequires:  perl-MogileFS-Utils
BuildRequires:  perl-Danga-Socket
BuildRequires:  perl(Sys::Syslog)
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

Provides:  MogileFS-Server = %{version}-%{release}
Obsoletes: MogileFS-Server < 2.17-5


%description
Server part of the MogileFS distributed filesystem


%package -n mogilefsd
Summary:        MogileFS tracker daemon
Group:          System Environment/Daemons
Requires:       initscripts
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires(pre):  shadow-utils
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
BuildRequires:  perl(Net::Netmask)
BuildRequires:  perl(DBD::mysql)

%description -n mogilefsd
The MogileFS tracker daemon mogilefsd

%prep
%setup -q -n MogileFS-Server-%{version}
rm -rf lib/Mogstored/
rm -f mogstored
rm -f mogautomount
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
%{__perl} Makefile.PL INSTALLDIRS=vendor
make %{?_smp_mflags}

%install
rm -rf %{buildroot}

make pure_install PERL_INSTALL_ROOT=%{buildroot}

find %{buildroot} -type f -name .packlist -exec rm -f {} \;
find %{buildroot} -depth -type d -exec rmdir {} 2>/dev/null \;

%{_fixperms} %{buildroot}/*

%{__install} -d -m0755 %{buildroot}%{_initrddir}
%{__install} -p -m0755 %{SOURCE2} %{buildroot}%{_initrddir}/mogilefsd

%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/mogilefs
%{__install} -p -m0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/mogilefs/mogilefsd.conf
%{__install} -p -m0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/mogilefs/mogilefs.conf

# remove the SQLite backend for now, since the latest driver
# is not in Fedora yet (#245699) and most people are probably
# only interested in the MySQL backend
# the PostgreSQL backend is not stable yet
rm %{buildroot}%{perl_vendorlib}/MogileFS/Store/SQLite.pm
rm %{buildroot}%{perl_vendorlib}/MogileFS/Store/Postgres.pm


%check
rm t/mogstored-shutdown.t
rm t/fid-stat.t
make test

%clean
rm -rf %{buildroot}

%pre -n mogilefsd
getent group mogilefsd >/dev/null || groupadd -r mogilefsd
getent passwd mogilesd >/dev/null || \
    useradd -r -g mogilefsd -d / -s /sbin/nologin \
    -c "MogileFS tracker daemon" mogilefsd
exit 0

%post -n mogilefsd
if [ $1 -eq 1 ]; then
    /sbin/chkconfig --add mogilefsd
fi


%preun -n mogilefsd
if [ $1 -eq 0 ]; then
    /sbin/service mogilefsd stop >/dev/null 2>&1 || :
    /sbin/chkconfig --del mogilefsd
fi

%files -n mogilefsd
%defattr(-,root,root,-)
%doc CHANGES TODO doc/
%{_bindir}/mogilefsd
%{_bindir}/mogdbsetup
%{_mandir}/man1/mogilefsd.*
%{_mandir}/man3/MogileFS::*.*
%{perl_vendorlib}/MogileFS/*
%dir %{perl_vendorlib}/MogileFS
%dir %{_sysconfdir}/mogilefs
%config(noreplace) %{_sysconfdir}/mogilefs/mogilefs.conf
%config(noreplace) %{_sysconfdir}/mogilefs/mogilefsd.conf
%{_initrddir}/mogilefsd

%changelog
* Mon Jun 10 2019 Dims <dims.main@gmail.com> 2.73-1
- Bump to upstream version
- Remove mogstored backends, use nginx dav luke!

* Mon Jan 19 2009 Ruben Kerkhof <ruben@rubenkerkhof.com> 2.30-1
- Upstream released new version

* Sun Nov 02 2008 Ruben Kerkhof <ruben@rubenkerkhof.com> 2.20-1
- Upstream released new version

* Wed Aug 13 2008 Ruben Kerkhof <ruben@rubenkerkhof.com> 2.17-7
- Add compat statements for subpackages

* Wed Aug 13 2008 Ruben Kerkhof <ruben@rubenkerkhof.com> 2.17-6
- Due to a problem in the tempfile handling, mogilefs occasionally 
  looses file data after a while. Bz 458890

* Sat Feb 09 2008 Ruben Kerkhof <ruben@rubenkerkhof.com> 2.17-5
- Rename package to respect the Naming Guidelines

* Sat Jan 19 2008 Ruben Kerkhof <ruben@rubenkerkhof.com> 2.17-4
- Require Perlbal instead of perlbal
- Remove autogenerated Perlbal dependency from mogstored

* Sat Jan 19 2008 Ruben Kerkhof <ruben@rubenkerkhof.com> 2.17-3
- Add Requires for perlbal to perlbal backend
- Rename package
- Remove failing test

* Thu Sep 06 2007 Ruben Kerkhof <ruben@rubenkerkhof.com> 2.17-2
- Add missing BRs (#252257)
* Sun May 20 2007 Ruben Kerkhof <ruben@rubenkerkhof.com> 2.17-1
- Initial import

