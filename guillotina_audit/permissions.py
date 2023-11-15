from guillotina import configure


configure.grant(role="guillotina.Manager", permission="audit.AccessContent")
