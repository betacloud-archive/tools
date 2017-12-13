#!/usr/bin/env python

import os_client_config
import shade
import yaml

CLOUDNAME = 'service'

#shade.simple_logging(debug=True, http_debug=True)

def set_quotaclass(project, quotaclass="default"):
    keystone = os_client_config.make_client('identity', cloud=CLOUDNAME)
    keystone.projects.update(project.id, **{"quotaclass": quotaclass})

def update_quota(project, cloud):
    print "update network quota for %s" % project.name
    cloud.set_network_quotas(project.id, **quotaclasses[project.quotaclass]["network"])

    print "update compute quota for %s" % project.name
    cloud.set_compute_quotas(project.id, **quotaclasses[project.quotaclass]["compute"])

    print "update volume quota for %s" % project.name
    cloud.set_volume_quotas(project.id, **quotaclasses[project.quotaclass]["volume"])

def check_quota(project, cloud):

    if "quotaclass" in project and project.name not in ["admin"]:

        quotanetwork = cloud.get_network_quotas(project.id)
        quotaupdate = False
        for key in quotaclasses[project.quotaclass]["network"]:
            if quotaclasses[project.quotaclass]["network"][key] != quotanetwork[key]:
                quotaupdate = True
                print "%s [ %s ] %d != %d" % (project.name, key, quotaclasses[project.quotaclass]["network"][key], quotanetwork[key])

        quotacompute = cloud.get_compute_quotas(project.id)
        for key in quotaclasses[project.quotaclass]["compute"]:
            if quotaclasses[project.quotaclass]["compute"][key] != quotacompute[key]:
                quotaupdate = True
                print "%s [ %s ] %d != %d" % (project.name, key, quotaclasses[project.quotaclass]["compute"][key], quotacompute[key])

        quotavolume = cloud.get_volume_quotas(project.id)
        for key in quotaclasses[project.quotaclass]["volume"]:
            if quotaclasses[project.quotaclass]["volume"][key] != quotavolume[key]:
                quotaupdate = True
                print "%s [ %s ] %d != %d" % (project.name, key, quotaclasses[project.quotaclass]["volume"][key], quotavolume[key])

        if quotaupdate:
            update_quota(project, cloud)

    elif "quotaclass" not in project and project.name not in ["admin"]:
        print "quotaclass not set for project %s, set quotaclass to default" % project.name
        set_quotaclass(project, "default")
        project = cloud.get_project(project.id)
        update_quota(project, cloud)


with open("quotaclasses.yml", "r") as fp:
    quotaclasses = yaml.load(fp)

cloud = shade.operator_cloud(cloud=CLOUDNAME)

for project in [p for p in cloud.search_projects() if not p.is_domain]:
    check_quota(project, cloud)
