NAME = python-rdoupdate
RPM_DIRS = --define "_sourcedir `pwd`/dist" \
           --define "_rpmdir `pwd`/dist" \
           --define "_specdir `pwd`" \
           --define "_builddir `pwd`/dist" \
           --define "_srcrpmdir `pwd`/dist"
 
all: srpm

dist:
	python setup.py sdist

rpm: dist $(NAME).spec
	rpmbuild $(RPM_DIRS) -ba $(NAME).spec

srpm: dist $(NAME).spec
	rpmbuild $(RPM_DIRS) -bs $(NAME).spec

.PHONY: dist rpm srpm
