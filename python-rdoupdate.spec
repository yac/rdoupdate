Name:             python-rdoupdate
Version:          0.10
Release:          1%{?dist}
Summary:          Manipulation and validation of YAML update files

Group:            Development/Languages
License:          ASL 2.0
URL:              https://github.com/yac/rdoupdate
Source0:          rdoupdate-%{version}.tar.gz

BuildArch:        noarch

BuildRequires:    python-setuptools
BuildRequires:    python2-devel

Requires:         python-setuptools
Requires:         python-argparse
Requires:         PyYAML
Requires:         git-core


%description
rdoupdate is a simple utility module useful for updating software repositories
using YAML update files optionally stored in a git repo.

rdoupdate-check script is provided which can validate if a file contains valid
update data and is able to extract such file from a git repo.


%prep
%setup -q -n rdoupdate-%{version}

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

%files
%doc README.md
%{_bindir}/rdoupdate
%{python_sitelib}/rdoupdate
%{python_sitelib}/*.egg-info

%changelog
* Fri Mar 21 2014 Jakub Ruzicka <jruzicka@redhat.com> 0.9
- Update to 0.9
- Update group support

* Wed Mar 19 2014 Jakub Ruzicka <jruzicka@redhat.com> 0.8
- Update to 0.8
- New koji-scratch build source

* Mon Mar 17 2014 Jakub Ruzicka <jruzicka@redhat.com> 0.7.2
- Update to 0.7.2

* Fri Feb 14 2014 Jakub Ruzicka <jruzicka@redhat.com> 0.7.1
- Update to 0.7.1

* Mon Feb 10 2014 Jakub Ruzicka <jruzicka@redhat.com> 0.7
- Update to 0.7

* Fri Jan 24 2014 Jakub Ruzicka <jruzicka@redhat.com> 0.5
- Update to 0.5

* Sat Jan 18 2014 Jakub Ruzicka <jruzicka@redhat.com> 0.4
- New backward incompatible version 0.4

* Mon Oct 07 2013 Jakub Ruzicka <jruzicka@redhat.com> 0.2
- Initial package.
