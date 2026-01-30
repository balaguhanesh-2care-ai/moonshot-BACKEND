// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://medscribealliance.github.io',
	base: '/scribe2fhir',
	integrations: [
		starlight({
			title: 'Scribe2FHIR Documentation',
			description: 'Comprehensive documentation for the Scribe2FHIR Python SDK',
			social: [{ 
				icon: 'github', 
				label: 'GitHub', 
				href: 'https://github.com/MedScribeAlliance/scribe2fhir' 
			}],
			sidebar: [
				{
					label: 'Getting Started',
					items: [
						{ label: 'Introduction', slug: 'introduction' },
						{ label: 'Installation', slug: 'installation' },
					],
				},
				{
					label: 'FHIR Specification',
					items: [
						{ label: 'FHIR Specification Documentation', slug: 'fhir-specification/readme' },
						{ label: 'Element Requirements', slug: 'fhir-specification/element_requirements' },
						{ label: 'Implementation Guide', slug: 'fhir-specification/implementation_guide' },
						{ label: 'SDK Specification', slug: 'fhir-specification/sdk_specification' },
					],
				},
				{
					label: 'Python SDK',
					items: [
						{ label: 'FHIR SDK Documentation', slug: 'python-sdk/readme' },
						{ label: 'Patient', slug: 'python-sdk/patient' },
						{ label: 'Encounter', slug: 'python-sdk/encounter' },
						{ label: 'Medical Condition', slug: 'python-sdk/medical_condition' },
						{ label: 'Vital Signs', slug: 'python-sdk/vital_signs' },
						{ label: 'Medication Prescription', slug: 'python-sdk/medication_prescription' },
						{ label: 'Medication History', slug: 'python-sdk/medication_history' },
						{ label: 'Allergy History', slug: 'python-sdk/allergy_history' },
						{ label: 'Family History', slug: 'python-sdk/family_history' },
						{ label: 'Immunization History', slug: 'python-sdk/immunization_history' },
						{ label: 'Procedure History', slug: 'python-sdk/procedure_history' },
						{ label: 'Procedure Ordering', slug: 'python-sdk/procedure_ordering' },
						{ label: 'Lab Findings', slug: 'python-sdk/lab_findings' },
						{ label: 'Lab Test Ordering', slug: 'python-sdk/lab_test_ordering' },
						{ label: 'Clinical Notes', slug: 'python-sdk/clinical_notes' },
						{ label: 'Examination Findings', slug: 'python-sdk/examination_findings' },
						{ label: 'Lifestyle History', slug: 'python-sdk/lifestyle_history' },
						{ label: 'Follow-up Appointment', slug: 'python-sdk/followup_appointment' },
						{ label: 'Patient Advice', slug: 'python-sdk/patient_advice' },
						{ label: 'Symptom', slug: 'python-sdk/symptom' },
					],
				},
				{
					label: 'Examples',
					autogenerate: { directory: 'examples' },
				},
			],
		}),
	],
});
