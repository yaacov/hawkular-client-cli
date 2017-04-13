%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

Name:           hawkular-client-cli
Version:        0.18.3
Release:        1%{?dist}
Summary:        Read/Write data to and from a Hawkular metric server.

License:        Apache License 2.0
URL:            https://github.com/yaacov/%{name}
Source0:        https://github.com/yaacov/%{name}/archive/v%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-devel
BuildRequires:  python-setuptools

Requires:       python-hawkular-client
Requires:       python-future
Requires:       PyYAML

%description
Utility script for accessing Hawkular metrics server remotely.


%prep
%setup -q


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT


%files
%doc README.md COPYING
%{_bindir}/hawkular-cli
%{python_sitelib}/*


%changelog
* Tue Mar 14 2017 yaacov <kobi.zamir@gmail.com> 0.16.3-1
- bump version (kobi.zamir@gmail.com)
- edit spec file (kobi.zamir@gmail.com)

* Wed Nov 09 2016 yaacov <kobi.zamir@gmail.com> 0.9.10-1
- bump version (kobi.zamir@gmail.com)
- edit spec file (kobi.zamir@gmail.com)

* Tue Nov 08 2016 yaacov <kobi.zamir@gmail.com> 0.9.9-1
- initial build

* Tue Nov 08 2016 yaacov <kobi.zamir@gmail.com> - 0.9.8-1
- initial build

* Tue Nov  8 2016 Yaacov Zamir <yzamir@redhat.com> - 0.9.7-1
- initial build
