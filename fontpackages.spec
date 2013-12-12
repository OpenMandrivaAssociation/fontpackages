%global spectemplatedir %{_sysconfdir}/rpmdevtools/
%global ftcgtemplatedir %{_datadir}/fontconfig/templates/
%global rpmmacrodir     %{_sysconfdir}/rpm/

Name:    fontpackages
Version: 1.44
Release: 9%{?dist}
Summary: Common directory and macro definitions used by font packages


# Mostly means the scriptlets inserted via this package do not change the
# license of the packages they're inserted in
License:   LGPLv3+
URL:       http://fedoraproject.org/wiki/fontpackages
Source0:   http://fedorahosted.org/releases/f/o/%{name}/%{name}-%{version}.tar.xz

BuildArch: noarch


%description
This package contains the basic directory layout, spec templates, rpm macros
and other materials used to create font packages.


%package filesystem
Summary: Directories used by font packages
License: Public Domain

%description filesystem
This package contains the basic directory layout used by font packages,
including the correct permissions for the directories.


%package devel
Summary: Templates and macros used to create font packages

Requires: rpmdevtools, %{name}-filesystem = %{version}-%{release}
Requires: fontconfig

%description devel
This package contains spec templates, rpm macros and other materials used to
create font packages.


%package tools
Summary: Tools used to check fonts and font packages

Requires: fontconfig, fontforge
Requires: curl, make, mutt
Requires: rpmlint

# repo-font-audit script need to run fedoradev-pkgowners command
# which is available on Fedora only and not on RHEL.
%if 0%{?fedora}
Requires: fedora-packager, yum-utils
%endif

%description tools
This package contains tools used to check fonts and font packages


%prep
%setup -q
%if 0%{?rhel}
sed -i 's|/usr/bin/fedoradev-pkgowners|""|g' bin/repo-font-audit
%endif

%build
for file in bin/repo-font-audit bin/compare-repo-font-audit ; do
sed -i "s|^DATADIR\([[:space:]]*\)\?=\(.*\)$|DATADIR=%{_datadir}/%{name}|g" \
  $file
done

%install
rm -fr %{buildroot}

# Pull macros out of macros.fonts and emulate them during install
for dir in fontbasedir        fontconfig_masterdir \
           fontconfig_confdir fontconfig_templatedir ; do
  export _${dir}=$(rpm --eval $(%{__grep} -E "^%_${dir}\b" \
    rpm/macros.fonts | %{__awk} '{ print $2 }'))
done

install -m 0755 -d %{buildroot}${_fontbasedir} \
                   %{buildroot}${_fontconfig_masterdir} \
                   %{buildroot}${_fontconfig_confdir} \
                   %{buildroot}${_fontconfig_templatedir} \
                   %{buildroot}%{spectemplatedir} \
                   %{buildroot}%{rpmmacrodir} \
                   %{buildroot}%{_datadir}/fontconfig/templates \
                   %{buildroot}/%_datadir/%{name} \
                   %{buildroot}%{_bindir}
install -m 0644 -p spec-templates/*.spec       %{buildroot}%{spectemplatedir}
install -m 0644 -p fontconfig-templates/*      %{buildroot}%{ftcgtemplatedir}
install -m 0644 -p rpm/macros*                 %{buildroot}%{rpmmacrodir}
install -m 0644 -p private/repo-font-audit.mk  %{buildroot}/%{_datadir}/%{name}
install -m 0755 -p private/core-fonts-report \
                   private/font-links-report \
                   private/fonts-report \
                   private/process-fc-query \
                   private/test-info           %{buildroot}/%{_datadir}/%{name}
install -m 0755 -p bin/*                       %{buildroot}%{_bindir}

cat <<EOF > %{name}-%{version}.files
%defattr(0644,root,root,0755)
%dir ${_fontbasedir}
%dir ${_fontconfig_masterdir}
%dir ${_fontconfig_confdir}
%dir ${_fontconfig_templatedir}
EOF

%clean
rm -fr %{buildroot}


%files filesystem -f %{name}-%{version}.files
%defattr(0644,root,root,0755)
%dir %{_datadir}/fontconfig

%files devel
%defattr(0644,root,root,0755)
%doc license.txt readme.txt
%config(noreplace) %{spectemplatedir}/*.spec
%{rpmmacrodir}/macros*
%dir %{ftcgtemplatedir}
%{ftcgtemplatedir}/*conf
%{ftcgtemplatedir}/*txt

%files tools
%defattr(0644,root,root,0755)
%doc license.txt readme.txt
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/repo-font-audit.mk
%defattr(0755,root,root,0755)
%{_datadir}/%{name}/core-fonts-report
%{_datadir}/%{name}/font-links-report
%{_datadir}/%{name}/fonts-report
%{_datadir}/%{name}/process-fc-query
%{_datadir}/%{name}/test-info
%{_bindir}/*
