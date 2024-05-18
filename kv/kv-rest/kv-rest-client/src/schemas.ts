export const $DBError = {
	properties: {
		detail: {
	properties: {
	},
},
		reason: {
	type: 'Enum',
	enum: ['db-error',],
	default: 'db-error',
},
	},
} as const;

export const $HTTPValidationError = {
	properties: {
		detail: {
	type: 'array',
	contains: {
		type: 'ValidationError',
	},
},
	},
} as const;

export const $InexistentItem = {
	properties: {
		key: {
	type: 'any-of',
	contains: [{
	type: 'string',
}, {
	type: 'null',
}],
},
		detail: {
	type: 'any-of',
	contains: [{
	properties: {
	},
}, {
	type: 'null',
}],
},
		reason: {
	type: 'Enum',
	enum: ['inexistent-item',],
	default: 'inexistent-item',
},
	},
} as const;

export const $InvalidData = {
	properties: {
		detail: {
	properties: {
	},
},
		reason: {
	type: 'Enum',
	enum: ['invalid-data',],
	default: 'invalid-data',
},
	},
} as const;

export const $Left_DBError_NoneType_ = {
	properties: {
		value: {
	type: 'all-of',
	contains: [{
	type: 'DBError',
}],
},
		tag: {
	type: 'Enum',
	enum: ['left',],
	default: 'left',
},
	},
} as const;

export const $Left_DBError_Sequence_str__ = {
	properties: {
		value: {
	type: 'all-of',
	contains: [{
	type: 'DBError',
}],
},
		tag: {
	type: 'Enum',
	enum: ['left',],
	default: 'left',
},
	},
} as const;

export const $Left_DBError_bool_ = {
	properties: {
		value: {
	type: 'all-of',
	contains: [{
	type: 'DBError',
}],
},
		tag: {
	type: 'Enum',
	enum: ['left',],
	default: 'left',
},
	},
} as const;

export const $Left_Union_DBError__InvalidData__InexistentItem__NoneType_ = {
	properties: {
		value: {
	type: 'any-of',
	contains: [{
	type: 'DBError',
}, {
	type: 'InvalidData',
}, {
	type: 'InexistentItem',
}],
},
		tag: {
	type: 'Enum',
	enum: ['left',],
	default: 'left',
},
	},
} as const;

export const $Left_Union_DBError__InvalidData__InexistentItem___A_ = {
	properties: {
		value: {
	type: 'any-of',
	contains: [{
	type: 'DBError',
}, {
	type: 'InvalidData',
}, {
	type: 'InexistentItem',
}],
},
		tag: {
	type: 'Enum',
	enum: ['left',],
	default: 'left',
},
	},
} as const;

export const $Left_Union_DBError__InvalidData__InexistentItem__tuple_str___A__ = {
	properties: {
		value: {
	type: 'any-of',
	contains: [{
	type: 'DBError',
}, {
	type: 'InvalidData',
}, {
	type: 'InexistentItem',
}],
},
		tag: {
	type: 'Enum',
	enum: ['left',],
	default: 'left',
},
	},
} as const;

export const $Right_DBError_NoneType_ = {
	properties: {
		value: {
	type: 'null',
},
		tag: {
	type: 'Enum',
	enum: ['right',],
	default: 'right',
},
	},
} as const;

export const $Right_DBError_Sequence_str__ = {
	properties: {
		value: {
	type: 'array',
	contains: {
	type: 'string',
},
},
		tag: {
	type: 'Enum',
	enum: ['right',],
	default: 'right',
},
	},
} as const;

export const $Right_DBError_bool_ = {
	properties: {
		value: {
	type: 'boolean',
},
		tag: {
	type: 'Enum',
	enum: ['right',],
	default: 'right',
},
	},
} as const;

export const $Right_Union_DBError__InvalidData__InexistentItem__NoneType_ = {
	properties: {
		value: {
	type: 'null',
},
		tag: {
	type: 'Enum',
	enum: ['right',],
	default: 'right',
},
	},
} as const;

export const $Right_Union_DBError__InvalidData__InexistentItem___A_ = {
	properties: {
		value: {
	properties: {
	},
},
		tag: {
	type: 'Enum',
	enum: ['right',],
	default: 'right',
},
	},
} as const;

export const $Right_Union_DBError__InvalidData__InexistentItem__tuple_str___A__ = {
	properties: {
		value: {
	type: 'unknown[]',
	maxItems: 2,
	minItems: 2,
},
		tag: {
	type: 'Enum',
	enum: ['right',],
	default: 'right',
},
	},
} as const;

export const $RootModel__A_ = {
	properties: {
	},
} as const;

export const $ValidationError = {
	properties: {
		loc: {
	type: 'array',
	contains: {
	type: 'any-of',
	contains: [{
	type: 'string',
}, {
	type: 'number',
}],
},
	isRequired: true,
},
		msg: {
	type: 'string',
	isRequired: true,
},
		type: {
	type: 'string',
	isRequired: true,
},
	},
} as const;