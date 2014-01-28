%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define name blackbird-memcached
%define version 0.1.3
%define unmangled_version %{version}
%define release 1%{dist}
%define include_dir /etc/blackbird/conf.d
%define plugins_dir /opt/blackbird/plugins

Summary: Get stats of memcached for blackbird by using "stats".
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: WTFPL
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: ARASHI, Jumpei <jumpei.arashi@arashike.com>
Packager: ARASHI, Jumpei <jumpei.arashi@arashike.com>
Requires: blackbird
Url: https://github.com/Vagrants/blackbird-memcached
BuildRequires:  python-setuptools

%description
UNKNOWN

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

install -dm 0755 $RPM_BUILD_ROOT%{include_dir}
install -dm 0755 $RPM_BUILD_ROOT%{plugins_dir}
install -p -m 0644 scripts/memcached.cfg $RPM_BUILD_ROOT%{include_dir}/memcached.cfg
install -p -m 0644 memcached.py $RPM_BUILD_ROOT%{plugins_dir}/memcached.py

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%dir %{include_dir}
%config(noreplace) %{include_dir}/memcached.cfg
%dir %{plugins_dir}
%{plugins_dir}/memcached.*

%changelog
* Tue Jan 27 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.1.3-1
- change method name(main loop) "looped_method" -> "build_items"

* Fri Jan 10 2014 makocchi <makocchi@gmial.com> - 0.1.2-1
- change gethostname to detect_hostname

* Mon Jan 06 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.1.1-3
- reduce file in %files "*" -> "memcached.*"

* Mon Jan 06 2014 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.1.1-2
- deploy /opt/blackbird/plugins/memcached.py

* Fri Nov 27 2013 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.1.1-1
- Include /etc/blackbird/conf.d/memcached.cfg

* Wed Nov 18 2013 ARASHI, Jumpei <jumpei.arashi@arashike.com> - 0.1.0-1
- Initial package
