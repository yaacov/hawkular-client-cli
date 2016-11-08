%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

Name:           hawkular-client-cli
Version:        0.9.9
Release:        1%{?dist}
Summary:        Virtual machines deployment tool

License:        GPLv2
URL:            https://github.com/yaacov/%{name}
Source0:        https://github.com/yaacov/%{name}/archive/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-devel
BuildRequires:  python-setuptools

Requires:       python-setuptools
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
%{_bindir}/hawkular-client-cli
%{python_sitelib}/*


%changelog
* Tue Nov 08 2016 yaacov <kobi.zamir@gmail.com> 0.9.9-1
- initial build

* Tue Nov 08 2016 yaacov <kobi.zamir@gmail.com> - 0.9.8-1
- initial build

* Tue Nov  8 2016 Yaacov Zamir <yzamir@redhat.com> - 0.9.7-1
- initial build
