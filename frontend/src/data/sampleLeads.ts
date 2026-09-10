export const sampleLeadCSV = `company,website,industry,employees,location,contact_name,contact_email
Stripe,https://stripe.com,FinTech,8000,USA,Patrick Collison,
Freshworks,https://www.freshworks.com,SaaS,5000,USA,Girish Mathrubootham,
Atlassian,https://www.atlassian.com,Software,12000,Australia,Mike Cannon-Brookes,
HubSpot,https://www.hubspot.com,SaaS,7500,USA,Yamini Rangan,
Twilio,https://www.twilio.com,Cloud Communications,8500,USA,Khozema Shipchandler,
Snowflake,https://www.snowflake.com,Cloud Computing,7000,USA,Sridhar Ramaswamy,
Datadog,https://www.datadoghq.com,Cloud Software,6200,USA,Thomas Graf,
Shopify,https://www.shopify.com,E-commerce,8000,Canada,Tobias Lutke,
GitLab,https://about.gitlab.com,DevOps,2200,USA,Sid Sijbrandij,`;

export const sampleICP = {
  target_industries: ["SaaS", "FinTech"],
  company_size_min: 100,
  company_size_max: 10000,
  target_locations: ["USA", "UK"],
  required_technologies: ["Python", "AWS"],
  target_business_models: ["B2B"],
  additional_criteria: [
    "Company should sell a technology product or service to business customers"
  ]
};