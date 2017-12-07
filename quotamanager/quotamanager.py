#!/usr/bin/env python

import os_client_config
import shade
import yaml

with open("quotaclasses.yml", "r") as fp:
    quotaclasses = yaml.load(fp)

#shade.simple_logging(debug=True, http_debug=True)

cloud = shade.operator_cloud(cloud='service')
keystone = os_client_config.make_client('identity', cloud='service')

for project in [p for p in cloud.search_projects() if not p.is_domain]:

    if "quotaclass" in project and project.name not in ["admin", "service"]:

        quotanetwork = cloud.get_network_quotas(project.id)
        quotaupdate = False
        for key in quotaclasses[project.quotaclass]["network"]:
            if quotaclasses[project.quotaclass]["network"][key] != quotanetwork[key]:
                quotaupdate = True
                print "%s [ %s ] %d != %d" % (project.name, key, quotaclasses[project.quotaclass]["network"][key], quotanetwork[key])
        if quotaupdate:
            print "update network quota for %s" % project.name
            cloud.set_network_quotas(project.id, **quotaclasses[project.quotaclass]["network"])

        quotacompute = cloud.get_compute_quotas(project.id)
        quotaupdate = False
        for key in quotaclasses[project.quotaclass]["compute"]:
            if quotaclasses[project.quotaclass]["compute"][key] != quotacompute[key]:
                quotaupdate = True
                print "%s [ %s ] %d != %d" % (project.name, key, quotaclasses[project.quotaclass]["compute"][key], quotacompute[key])
        if quotaupdate:
            print "update compute quota for %s" % project.name
            cloud.set_compute_quotas(project.id, **quotaclasses[project.quotaclass]["compute"])

        quotavolume = cloud.get_volume_quotas(project.id)
        quotaupdate = False
        for key in quotaclasses[project.quotaclass]["volume"]:
            if quotaclasses[project.quotaclass]["volume"][key] != quotavolume[key]:
                quotaupdate = True
                print "%s [ %s ] %d != %d" % (project.name, key, quotaclasses[project.quotaclass]["volume"][key], quotavolume[key])
        if quotaupdate:
            print "update volume quota for %s" % project.name
            cloud.set_volume_quotas(project.id, **quotaclasses[project.quotaclass]["volume"])

    elif "quotaclass" not in project and project.name not in ["admin", "service"]:
        print "quotaclass not set for project %s, set quotaclass to default" % project.name
        keystone.projects.update(project.id, **{"quotaclass": "default"})
