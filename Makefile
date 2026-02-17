.PHONY: all individual

all: individual

individual:
	$(MAKE) -C $@
