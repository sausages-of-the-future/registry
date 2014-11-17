Users are separate from people (you should see Users as a proxy for a proper verify / auth system)

The registries should be demonstrably generated directly from code.

What if some registers, eg births, were split up among different orgs (eg local councils)

Licence registers are probably split up by category, but for now done as a single one.

Standard rest interfaces are hard eg you dont want to do /user/licences
or licences/user. Instead use scope of requests to limit? eg sometimes a
get just validates, sometimes it provides all details?
