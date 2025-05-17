// frontend/src/admin/pages/AdminTableManagerPage.js
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
// 确保 Typography 已导入
import { Table, Button, Modal, Form, Input, Select, Spin, Alert, Popconfirm, message, Space, DatePicker, InputNumber, Checkbox, Typography } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { 
    getTableSchema, 
    getTableData, 
    addTableRecord, 
    updateTableRecord, 
    deleteTableRecord 
} from '../services/adminApi';
import moment from 'moment';

const { Option } = Select;
const { Title } = Typography; // 解构 Title

// Helper function to render form fields based on schema (保持不变)
const renderFormField = (fieldSchema) => {
    // ... (之前的 renderFormField 代码)
    const { name, label, type, required, placeholder, options, defaultValue } = fieldSchema;
    let rules = [];
    if (required) {
        rules.push({ required: true, message: `${label || name} is required!` });
    }
    if (type === 'email') {
        rules.push({ type: 'email', message: 'Please enter a valid email!' });
    }
    if (type === 'url') {
        rules.push({ type: 'url', message: 'Please enter a valid URL!' });
    }
    
    let inputNode;
    switch (type) {
        case 'password':
            inputNode = <Input.Password placeholder={placeholder || `Enter ${label || name}`} />;
            break;
        case 'number':
        case 'integer':
        case 'bigint':
            inputNode = <InputNumber style={{ width: '100%' }} placeholder={placeholder || `Enter ${label || name}`} />;
            break;
        case 'boolean':
            return (
                <Form.Item
                    key={name}
                    name={name}
                    valuePropName="checked"
                    label={label || name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    rules={rules}
                    initialValue={defaultValue || false}
                >
                    <Checkbox />
                </Form.Item>
            );
        case 'date':
        case 'datetime':
            inputNode = <DatePicker showTime={type === 'datetime'} format={type === 'datetime' ? "YYYY-MM-DD HH:mm:ss" : "YYYY-MM-DD"} style={{ width: '100%' }} placeholder={placeholder || `Select ${label || name}`} />;
            break;
        case 'select':
            inputNode = (
                <Select placeholder={placeholder || `Select ${label || name}`}>
                    {(options || []).map(opt => <Option key={opt.value} value={opt.value}>{opt.label}</Option>)}
                </Select>
            );
            break;
        case 'textarea':
            inputNode = <Input.TextArea rows={3} placeholder={placeholder || `Enter ${label || name}`} />;
            break;
        case 'text':
        case 'varchar':
        case 'email':
        case 'url':
        default:
            inputNode = <Input placeholder={placeholder || `Enter ${label || name}`} />;
    }

    return (
        <Form.Item
            key={name}
            label={label || name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            name={name}
            rules={rules}
            initialValue={defaultValue}
        >
            {inputNode}
        </Form.Item>
    );
};


const AdminTableManagerPage = () => {
    const { tableName } = useParams();

    const [schema, setSchema] = useState(null);
    const [data, setData] = useState([]);
    const [primaryKey, setPrimaryKey] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    const [isModalVisible, setIsModalVisible] = useState(false);
    const [editingRecord, setEditingRecord] = useState(null);
    const [form] = Form.useForm();
    const [modalLoading, setModalLoading] = useState(false);

    const loadSchemaAndData = useCallback(async () => {
        if (!tableName) return;
        setIsLoading(true);
        setError(null);
        try {
            const schemaData = await getTableSchema(tableName);
            if (!schemaData || !schemaData.columns_for_display) {
                throw new Error(`Schema not found or invalid for table ${tableName}`);
            }
            setSchema(schemaData);
            setPrimaryKey(schemaData.primary_key || '');

            const tableDataResponse = await getTableData(tableName);
            setData(tableDataResponse.data || []);
        } catch (err) {
            console.error(`Failed to load data for table ${tableName}:`, err);
            const errorMsg = err.msg || `Could not load data for ${tableName}`;
            setError(errorMsg);
            message.error(errorMsg);
        } finally {
            setIsLoading(false);
        }
    }, [tableName]);

    useEffect(() => {
        loadSchemaAndData();
    }, [loadSchemaAndData]);

    const handleAdd = () => {
        setEditingRecord(null);
        form.resetFields();
        const defaultValues = {};
        schema?.form_fields_add?.forEach(fieldName => {
            const fieldDef = schema.all_columns?.find(c => c.name === fieldName);
            if (fieldDef && fieldDef.defaultValue !== undefined) {
                defaultValues[fieldName] = fieldDef.defaultValue;
            }
            if ((fieldDef?.type === 'date' || fieldDef?.type === 'datetime') && defaultValues[fieldName]) {
                defaultValues[fieldName] = moment(defaultValues[fieldName]);
            }
        });
        form.setFieldsValue(defaultValues);
        setIsModalVisible(true);
    };

    const handleEdit = (record) => {
        setEditingRecord(record);
        const formValues = { ...record };
        schema?.editable_fields?.forEach(fieldName => {
            const fieldDef = schema.all_columns?.find(c => c.name === fieldName);
            if ((fieldDef?.type === 'date' || fieldDef?.type === 'datetime') && formValues[fieldName]) {
                formValues[fieldName] = moment(formValues[fieldName]);
            }
            if (fieldDef?.type === 'boolean' && formValues[fieldName] !== undefined) {
                formValues[fieldName] = !!formValues[fieldName];
            }
        });
        form.setFieldsValue(formValues);
        setIsModalVisible(true);
    };

    const handleDelete = async (recordId) => {
        if (!primaryKey || recordId === undefined) {
            message.error("Cannot delete record: Primary key or record ID is missing.");
            return;
        }
        try {
            await deleteTableRecord(tableName, recordId);
            message.success('Record deleted successfully');
            loadSchemaAndData();
        } catch (err) {
            message.error(err.msg || 'Failed to delete record');
        }
    };

    const handleModalOk = async () => {
        try {
            const values = await form.validateFields();
            setModalLoading(true);
            const processedValues = { ...values };
            schema?.all_columns?.forEach(colDef => {
                if ((colDef.type === 'date' || colDef.type === 'datetime') && processedValues[colDef.name] && moment.isMoment(processedValues[colDef.name])) {
                    processedValues[colDef.name] = processedValues[colDef.name].toISOString();
                }
            });

            if (editingRecord && primaryKey) {
                await updateTableRecord(tableName, editingRecord[primaryKey], processedValues);
                message.success('Record updated successfully');
            } else {
                await addTableRecord(tableName, processedValues);
                message.success('Record added successfully');
            }
            setIsModalVisible(false);
            loadSchemaAndData();
        } catch (errInfo) {
            if (errInfo.errorFields) {
                message.error('Please correct the form errors.');
            } else {
                message.error(errInfo.msg || 'Failed to save record');
            }
        } finally {
            setModalLoading(false);
        }
    };

    const handleModalCancel = () => {
        setIsModalVisible(false);
    };

    const tableColumns = useMemo(() => {
        if (!schema?.columns_for_display) return [];
        return [
            ...schema.columns_for_display.map(colName => ({
                title: colName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                dataIndex: colName,
                key: colName,
                sorter: (a, b) => {
                    if (a[colName] < b[colName]) return -1;
                    if (a[colName] > b[colName]) return 1;
                    return 0;
                },
                render: (text, record) => {
                    const colDef = schema.all_columns?.find(c => c.name === colName);
                    if (colDef?.type === 'boolean') return <Checkbox checked={!!text} disabled />;
                    if ((colDef?.type === 'date' || colDef?.type === 'datetime') && text) return moment(text).format(colDef.type === 'datetime' ? 'YYYY-MM-DD HH:mm:ss' : 'YYYY-MM-DD');
                    return String(text === null || text === undefined ? '' : text);
                }
            })),
            {
                title: 'Actions',
                key: 'actions',
                fixed: 'right',
                width: 150,
                render: (_, record) => (
                    <Space size="small">
                        <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>Edit</Button>
                        <Popconfirm
                            title="Are you sure to delete this record?"
                            onConfirm={() => handleDelete(record[primaryKey])}
                            okText="Yes"
                            cancelText="No"
                        >
                            <Button type="link" danger icon={<DeleteOutlined />}>Delete</Button>
                        </Popconfirm>
                    </Space>
                ),
            },
        ];
    }, [schema, primaryKey, handleEdit, handleDelete]); // handleEdit, handleDelete 是稳定的，但作为依赖项是好习惯

    const formFieldsForModal = useMemo(() => {
        if (!schema) return [];
        const fieldNames = editingRecord ? schema.editable_fields : schema.form_fields_add;
        return fieldNames?.map(fieldName => {
            const fieldDef = schema.all_columns?.find(col => col.name === fieldName) || { name: fieldName, label: fieldName, type: 'text', required: false };
            return renderFormField({ ...fieldDef, label: fieldDef.label || fieldName });
        }) || [];
    }, [schema, editingRecord]);

    if (isLoading && !isModalVisible) return <Spin tip={`Loading ${tableName}...`} style={{ display: 'block', marginTop: 50 }}><div style={{height: 200}} /></Spin>;
    if (error && !isModalVisible) return <Alert message={`Error: ${error}`} type="error" showIcon />;
    if (!schema && !isLoading) return <Alert message={`Schema not found for table '${tableName}'.`} type="warning" showIcon />;

    return (
        <div>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                {/* Title 已导入并解构 */}
                <Title level={3} style={{ margin: 0 }}>{schema?.table_name_display || tableName}</Title>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
                    Add Record
                </Button>
            </div>
            <Table
                columns={tableColumns}
                dataSource={data}
                rowKey={record => record[primaryKey] || JSON.stringify(record)}
                loading={isLoading}
                bordered
                size="middle"
                scroll={{ x: 'max-content' }}
                pagination={{ pageSize: 10, showSizeChanger: true, pageSizeOptions: ['10', '20', '50'] }}
            />
            <Modal
                title={editingRecord ? `Edit Record (ID: ${editingRecord && primaryKey ? editingRecord[primaryKey] : 'N/A'})` : `Add New Record to ${schema?.table_name_display}`}
                open={isModalVisible}
                onOk={handleModalOk}
                onCancel={handleModalCancel}
                confirmLoading={modalLoading}
                destroyOnClose
                width={schema?.modal_width || 720}
                maskClosable={false}
            >
                <Form form={form} layout="vertical" name="recordForm">
                    {formFieldsForModal}
                </Form>
            </Modal>
        </div>
    );
};

export default AdminTableManagerPage;
